import requests
import json
import random
import string
import itertools

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
        print("Processing", data['api'])
        self.data = data

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

    def __publicResource(self):
        return f'{self.data["api"]}/{self.data["public"]}'

    def __testPublic(self):
        resource = self.__publicResource()
        response = requests.get(resource, headers={'x-api-key': self.data['api_key']})
        return self.__testStatusCode(response.status_code, 200, f'Public resource {self.data["public"]}')

    def __testProtected(self):
        result = []
        resource = f'{self.data["api"]}/{self.data["protected"]}'
        response = requests.get(resource, headers={
                'x-api-key': self.data['api_key'],
                'Authorization': f'Bearer {self.access_token}'
            }
        )
        result.append(self.__testStatusCode(response.status_code, 200, f'Protected resource {self.data["protected"]}'))
        response = requests.get(resource, headers={
                'x-api-key': self.data['api_key']
            }
        )
        result.append(self.__testStatusCode(response.status_code, [401, 403, 404], f'Without Authorization header {self.data["protected"]}'))
        # tamper with integrity access token
        accessToken = self.access_token[0:-1]
        response = requests.get(resource, headers={
                        'x-api-key': self.data['api_key'],
                        'Authorization': f'Bearer {accessToken}'
                    }
                )
        result.append(self.__testStatusCode(response.status_code, [401, 403, 404], f'With corrupt access token {self.data["protected"]}'))
        return result

    def __testNoApiKey(self):
        # we assume that, if the public resource is protected with an API key,
        # so are the others. For a production API, this is not a reasonable assumption.
        # In the context of testing whether students understand how to use API keys,
        # the assumption is OK.
        resource = self.__publicResource()
        response = requests.get(self.__publicResource())
        return self.__testStatusCode(response.status_code, [403, 404], f'Without API key {self.data["public"]}')

    def __testMethodRejected(self, method):
        resource = self.__publicResource()
        key = self.data['api_key']
        response = method['function'](resource, key)
        return self.__testStatusCode(response.status_code, [403, 404, 405], f'Using unsupported method, {method["verb"]}')

    def __metadata(self, url):
        return json.loads(requests.get(f'{url}/.well-known/openid-configuration').text)

    def assess(self):
        if self.__valid():
            forbidden_methods = [
                {'verb': 'PUT', 'function': lambda url, key: requests.put(url, headers={'x-api-key': key})},
                {'verb': 'DELETE', 'function': lambda url, key: requests.delete(url, headers={'x-api-key': key})},
                {'verb': 'PATCH', 'function': lambda url, key: requests.patch(url, headers={'x-api-key': key})},
                {'verb': 'POST', 'function': lambda url, key: requests.post(url, headers={'x-api-key': key})}
            ]
            rest_api_assess = [
                self.__testPublic(),
                self.__testNoApiKey()
            ] + [self.__testMethodRejected(method) for method in forbidden_methods]
            try:
                self.openidConfiguration = self.__metadata(self.data['iss'])
            except requests.exceptions.ConnectionError:
                rest_api_assess.append(TestFailure(f'cannot connect to issuer at {self.data["iss"]}'))
            try:
                self.token_endpoint = self.openidConfiguration["token_endpoint"]
            except KeyError:
                rest_api_assess.append(TestFailure(f'no metadata found at issuer ({self.data["iss"]})'))
            try:
                self.accessTokenResponse = json.loads(requests.post(
                    self.token_endpoint,
                    {
                        "client_id": self.data["client_id"],
                        "client_secret": self.data["client_secret"],
                        "grant_type": 'client_credentials'
                    }
                ).text)
                self.access_token = self.accessTokenResponse['access_token']
            except KeyError:
                rest_api_assess.append(TestFailure(f'cannot retrieve access token: {self.accessTokenResponse["error"]}'))
            except:
                print('unexpected error. Please send author your command line and data.json.')
                return

            rest_api_assess = rest_api_assess + self.__testProtected()

            failures = itertools.filterfalse(lambda result: isinstance(result, TestSuccess), rest_api_assess)
            success = True
            for result in failures:
                print(f'fail: {result.message}')
                success = False
            print("pass" if success else "fail")
        else:
            print("fail")
