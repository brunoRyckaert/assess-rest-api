import requests
import json
import itertools
import sys
import traceback

class TestResult:
    def __init__(self, msg):
        self.message = msg

class TestFailure(TestResult): pass

class TestSuccess(TestResult): pass

class TestRun:

    mandatory_keys = [
        'owner',
        'api_key',
        'api',
        'resource'
    ]

    keys_for_authenticated_apis = [
        'iss',
        'client_secret',
        'client_id'
    ]

    keys_for_scoped_apis = [
        'audience'
    ]

    methods = {'GET': lambda url, headers: requests.get(url, headers=headers),
               'PUT': lambda url, headers: requests.put(url, headers=headers),
               'DELETE': lambda url, headers: requests.delete(url, headers=headers),
               'PATCH': lambda url, headers: requests.patch(url, headers=headers),
               'POST': lambda url, headers: requests.post(url, headers=headers),
               'HEAD': lambda url, headers: requests.head(url, headers=headers)}

    http_verbs = list(methods.keys())

    def __init__(self, data):
        print(f'Processing {data["owner"]}\'s API')
        self.data = data
        self.rest_api_assess = []
        self.token_endpoint = None

    def __valid(self):
        result = True
        missing_keys = itertools.filterfalse(lambda k: k in self.data, self.mandatory_keys)
        if self.__authenticationRequired():
            missing_keys = itertools.chain(missing_keys,
                itertools.filterfalse(lambda k: k in self.data, self.keys_for_authenticated_apis))
        for key in missing_keys:
            print(f'{key} is not set in data file.')
            result = False
        if not ('authenticated' in self.data or 'public' in self.data):
            print('an API must have public or authenticated methods, or both - neither key is present in data file.')
            result = False
        else:
            result = result and self.__checkMethods()
        return result

    def __checkMethods(self):
        result = True
        if 'public' in self.data:
            public = self.data['public']
            if not isinstance(public, list) or len(public) == 0:
                print('public field should be a non-empty list of HTTP verbs')
                result = False
            for verb in public:
                if verb not in self.http_verbs:
                    print(f'public field: {verb} is not a supported HTTP verb.')
                    result = False
        if 'authenticated' in self.data:
            authenticated = self.data['authenticated']
            if not isinstance(authenticated, dict) or len(authenticated) == 0:
                print('authenticated field should be a map of HTTP verbs to scopes, e.g. {"GET": "", "PUT": "rides/update"}')
                result = False
            else:
                for verb in authenticated.keys():
                    if not verb in self.http_verbs:
                        print(f'authenticated field: {verb} is not recognized as an HTTP verb. Only use one of {self.http_verbs}')
                        result = False
                    else:
                        if not isinstance(authenticated[verb], str):
                            print(f'authenticated field: value of {verb} must be a string expressing a scope')
                            result = False
        return result

    def __testStatusCode(self, actual, acceptable, testDesc):
        if isinstance(acceptable, list) and actual not in acceptable:
            return TestFailure(f'{testDesc} returns status code {actual}. Expected is one of {acceptable}.')
        if isinstance(acceptable, int) and actual != acceptable:
            return TestFailure(f'{testDesc} returns status code {actual}. Expected is {acceptable}.')
        return TestSuccess(f'{testDesc} returns status code {actual}.')

    def __sendRequest(self, method, resource, headers):
        try:
            call = self.methods[method]
            return call(resource, headers)
        except:
            self.rest_api_assess.append(TestFailure(f'cannot {method} on {resource}'))
            raise

    def __testResource(self, method, resource, token='', scope=''):
        headers = {
            'x-api-key': self.data['api_key'],
            'Authorization': f'Bearer {token}'
        }
        try:
            response = self.__sendRequest(method, resource, headers)
            return self.__testStatusCode(
                response.status_code,
                [200, 201],
                (f'With scope {scope}, ' if scope != '' else '') + f'{method} {self.data["resource"]}'
            )
        except Exception as e:
            return TestFailure(e)

    def __testNoApiKey(self, method, resource, token=''):
        headers = {
            'Authorization': f'Bearer {token}'
        }
        try:
            response = self.__sendRequest(method, resource, headers)
            return self.__testStatusCode(response.status_code, [403, 404], f'Without API key {method} {self.data["resource"]}')
        except Exception as e:
            return TestFailure(e)

    def __testNoToken(self, method, resource):
        headers = {'x-api-key': self.data['api_key']}
        response = self.__sendRequest(method, resource, headers)
        return self.__testStatusCode(response.status_code, [401, 403, 404], f'Without Authorization header {method} {self.data["resource"]}')

    def __testCorruptToken(self, method, resource, token):
        headers = {
            'x-api-key': self.data['api_key'],
            'Authorization': f'Bearer {token[0:-1]}'
        }
        response = self.__sendRequest(method, resource, headers)
        return self.__testStatusCode(response.status_code, [401, 403, 404, 500], f'With corrupt access token {method} {self.data["resource"]}')

    def __testWrongScope(self, method, resource, accessToken, scope):
        headers = {
            'x-api-key': self.data['api_key'],
            'Authorization': f'Bearer {accessToken}'
        }
        response = self.__sendRequest(method, resource, headers)
        return self.__testStatusCode(response.status_code, [401, 403, 404], f'With scope {scope}, {method} {self.data["resource"]}')

    def __testMethodRejected(self, resource, method, token=''):
        headers = {
            'x-api-key': self.data['api_key'],
            'Authorization': f'Bearer {token}'
        }
        try:
            if self.__authenticationRequired():
                headers['Authorization'] = f'Bearer  {self.__getAccessToken()}'
            response = self.methods[method](resource, headers)
            return self.__testStatusCode(response.status_code, [403, 404, 405], f'Using unsupported method - {method}')
        except Exception as e:
            return TestFailure(e)

    def __metadata(self, url):
        try:
            response = requests.get(f'{url}/.well-known/openid-configuration')
            if response.status_code == requests.codes.ok:
                return json.loads(response.text)
            else:
                raise Exception(f'no metadata found at issuer ({self.data["iss"]})')
        except:
            raise

    def __getAccessToken(self, scope=''):
        params = {
            "client_id": self.data["client_id"],
            "client_secret": self.data["client_secret"],
            "grant_type": 'client_credentials'
        }
        # audience is ignored by Cognito, but is required by Auth0
        if 'audience' in self.data:
            params['audience'] = self.data['audience']
        else:
            params['audience'] = f'{self.data["api"]}/{self.data["resource"]}'
        params['scope'] = scope
        if self.token_endpoint is None:
            try:
                openidConfiguration = self.__metadata(self.data['iss'])
                self.token_endpoint = openidConfiguration["token_endpoint"]
            except requests.exceptions.ConnectionError:
                self.rest_api_assess.append(TestFailure(f'cannot connect to issuer at {self.data["iss"]}'))
                raise
            except:
                self.rest_api_assess.append(TestFailure(f'no metadata found at issuer ({self.data["iss"]})'))
                raise
        try:
            accessTokenResponse = json.loads(requests.post(
                self.token_endpoint,
                params
            ).text)
            return accessTokenResponse['access_token']
        except KeyError:
            self.rest_api_assess.append(TestFailure(f'cannot retrieve access token with scope {scope}'))
            pass
        except:
            print(f'unexpected error: {sys.exc_info()[0]}. Please send author your command line and data.json.')
            raise

    def __authenticationRequired(self):
        return ('authenticated' in self.data)

    def assess(self):
        if self.__valid():
            resource = f'{self.data["api"]}/{self.data["resource"]}'
            public_methods = [] if 'public' not in self.data else self.data['public']
            authenticated_methods = [] if 'authenticated' not in self.data else [method for method in self.data['authenticated']]
            exposed_methods = public_methods + authenticated_methods
            forbidden_methods = [verb for verb in self.http_verbs if verb not in exposed_methods]
            for method in public_methods:
                self.rest_api_assess.append(self.__testResource(method, resource))
                self.rest_api_assess.append(self.__testNoApiKey(method, resource))
            if self.__authenticationRequired():
                scopes = {scope for scope in self.data['authenticated'].values() if scope != ''}
                accessTokens = {}
                try:
                    accessTokens = {scope: self.__getAccessToken(scope) for scope in scopes}
                    accessTokens[''] = self.__getAccessToken()
                    for method, scope in self.data['authenticated'].items():
                        self.rest_api_assess.append(self.__testResource(method, resource, token=accessTokens[scope], scope=scope))
                        self.rest_api_assess.append(self.__testNoApiKey(method, resource, token=accessTokens[scope]))
                        self.rest_api_assess.append(self.__testNoToken(method, resource))
                        self.rest_api_assess.append(self.__testCorruptToken(method, resource, accessTokens[scope]))
                        for scp in scopes:
                            if scope != '':
                                if scp != scope:
                                    self.rest_api_assess.append(self.__testWrongScope(method, resource, accessTokens[scp], scp))
                            else:
                                self.rest_api_assess.append(self.__testResource(method, resource, token=accessTokens[scp], scope=scp))
                except:
                    pass
            self.rest_api_assess += [self.__testMethodRejected(resource, method) for method in forbidden_methods]

            failures = itertools.filterfalse(lambda result: isinstance(result, TestSuccess), self.rest_api_assess)
            successes = [success for success in self.rest_api_assess if isinstance(success, TestSuccess)]
            success = True
            for result in successes:
                print(f'pass: {result.message}')
            for result in failures:
                print(f'fail: {result.message}')
                success = False
            print(f'{len(self.rest_api_assess)} tests')
            print("pass" if success else "fail")
        else:
            print("fail")
