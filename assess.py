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

    keys = [
        'owner',
        'api_key',
        'api',
        'public',
        'protected',
        'iss',
        'client_secret',
        'client_id'
        ]

    def __init__(self, data):
        print(f'Processing {data["owner"]}\'s API')
        self.data = data
        self.access_token = ''

    def __valid(self):
        result = True
        missing_keys = itertools.filterfalse(lambda k: k in self.data, self.keys)
        for key in missing_keys:
            print(f'{key} is not set in data file.')
            result = False
        return result

    def __testStatusCode(self, actual, acceptable, testDesc):
        if isinstance(acceptable, list) and actual not in acceptable:
            return TestFailure(f'{testDesc} returns status code {actual}. Expected is one of {acceptable}.')
        if isinstance(acceptable, int) and actual != acceptable:
            return TestFailure(f'{testDesc} returns status code {actual}. Expected is {acceptable}.')
        return TestSuccess(f'{testDesc} returns status code {actual}.')

    def __testResource(self, resource):
        headers = {'x-api-key': self.data['api_key']}
        if len(self.access_token) > 0:
            headers['Authorization'] = f'Bearer {self.access_token}'
        response = requests.get(resource, headers=headers)
        return self.__testStatusCode(response.status_code, 200, f'{resource.split("/")[-1]}')

    def __testProtected(self, resource):
        result = []
        result.append(self.__testResource(resource))
        response = requests.get(resource, headers={
                'x-api-key': self.data['api_key']
            }
        )
        result.append(self.__testStatusCode(response.status_code, [401, 403, 404], f'Without Authorization header {self.data["protected"]}'))
        # tamper with integrity access token
        response = requests.get(resource, headers={
                        'x-api-key': self.data['api_key'],
                        'Authorization': f'Bearer {self.access_token[0:-1]}'
                    }
                )
        result.append(self.__testStatusCode(response.status_code, [401, 403, 404], f'With corrupt access token {self.data["protected"]}'))
        return result

    def __testNoApiKey(self, resource):
        headers = {}
        if len(self.access_token) > 0:
            headers['Authorization'] = f'Bearer {self.access_token}'
        response = requests.get(resource, headers=headers)
        return self.__testStatusCode(response.status_code, [403, 404], f'Without API key {resource.split("/")[-1]}')

    def __testMethodRejected(self, resource, method):
        headers = {'x-api-key': self.data['api_key']}
        if len(self.access_token) > 0:
            headers['Authorization'] = f'Bearer self.access_token'
        response = method['function'](resource, headers)
        return self.__testStatusCode(response.status_code, [403, 404, 405], f'Using unsupported method, {method["verb"]}')

    def __metadata(self, url):
        return json.loads(requests.get(f'{url}/.well-known/openid-configuration').text)

    def __getAccessToken(self):
        params = {
            "client_id": self.data["client_id"],
            "client_secret": self.data["client_secret"],
            "grant_type": 'client_credentials'
        }
        # audience is ignored by Cognito, but is required by Auth0
        if 'audience' in self.data:
            params['audience'] = self.data['audience']
        else:
            params['audience'] = f'{self.data["api"]}/{self.data["protected"]}'
        try:
            self.openidConfiguration = self.__metadata(self.data['iss'])
            self.token_endpoint = self.openidConfiguration["token_endpoint"]
        except requests.exceptions.ConnectionError:
            self.rest_api_assess.append(TestFailure(f'cannot connect to issuer at {self.data["iss"]}'))
            raise
        except KeyError:
            self.rest_api_assess.append(TestFailure(f'no metadata found at issuer ({self.data["iss"]})'))
            raise
        try:
            self.accessTokenResponse = json.loads(requests.post(
                self.token_endpoint,
                params
            ).text)
            self.access_token = self.accessTokenResponse['access_token']
            return
        except KeyError:
            self.rest_api_assess.append(TestFailure(f'cannot retrieve access token: {self.accessTokenResponse["error"]}'))
            raise
        except:
            print(f'unexpected error: {sys.exc_info()[0]}. Please send author your command line and data.json.')
            raise

    def assess(self):
        if self.__valid():
            public_resource = f'{self.data["api"]}/{self.data["public"]}'
            protected_resource = f'{self.data["api"]}/{self.data["protected"]}'
            forbidden_methods = [
                {'verb': 'PUT', 'function': lambda url, headers: requests.put(url, headers=headers)},
                {'verb': 'DELETE', 'function': lambda url, headers: requests.delete(url, headers=headers)},
                {'verb': 'PATCH', 'function': lambda url, headers: requests.patch(url, headers=headers)},
                {'verb': 'POST', 'function': lambda url, headers: requests.post(url, headers=headers)}
            ]
            # test public resource
            self.rest_api_assess = [
                self.__testResource(public_resource),
                self.__testNoApiKey(public_resource)
            ] + [self.__testMethodRejected(public_resource, method) for method in forbidden_methods]
            # test protected resource
            try:
                self.__getAccessToken()
                self.rest_api_assess = self.rest_api_assess + [
                    self.__testNoApiKey(protected_resource)
                    ] + self.__testProtected(protected_resource) + [
                    self.__testMethodRejected(protected_resource, method) for method in forbidden_methods
                    ]
            except:
                #print(f'cannot get access token - {sys.exc_info()[0].__name__}: {sys.exc_info()[1]}')
                #traceback.print_tb(sys.exc_info()[2])
                pass

            failures = itertools.filterfalse(lambda result: isinstance(result, TestSuccess), self.rest_api_assess)
            success = True
            for result in failures:
                print(f'fail: {result.message}')
                success = False
            print("pass" if success else "fail")
        else:
            print("fail")
