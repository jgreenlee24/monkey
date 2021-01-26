import boto3


class SSMParameterStoreError(Exception):
    pass


class SSMParameterStore:
    """Provides an interface into AWS SSM Parameter Store.
    All parameters in SSM should be prefixed by the environment that they belong.
    """

    def __init__(self, env, **kwargs):
        self._env = env
        self._ssm = boto3.client('ssm', **kwargs)

    def fetch(self, key, required=True):
        """Fetches a single parameter.
        Arguments:
            key {str} -- The name of the parameter.
            required {bool} -- Whether or not the parameter is required.
        Raises:
            SSMParameterStoreError -- When required is True and the parameter is missing.
        Examples:
            >>> param_store = SSMParameterStore('dev')
            >>> param = param_store.fetch('/ltk-follower-service/log-level')
        """

        name = f'/{self._env}{key}'

        response = self._ssm.get_parameters(
            Names=[name], WithDecryption=True,
        )

        try:
            return response['Parameters'][0]['Value']
        except IndexError:
            if not required:
                return None

            raise SSMParameterStoreError(
                f'Parameter "{key}" not found in {self._env}'
            )

    def fetch_many(self, required=None, optional=None):
        """Fetches multiple parameters.
        Arguments:
            required {list} -- Required parameters.
            optional {list} -- Optional parameters.
        Returns:
            dict: The parameters found in SSM.
        Raises:
            SSMParameterStoreError -- When a required parameter is missing.
        Examples:
            >>> param_store = SSMParameterStore('dev')
            >>> params = param_store.fetch_many(
            ...     required=['/my-service/param1', '/my-service/param2'],
            ...     optional=['/my-service/param3']
            ... )
        """

        params = {}

        if not required:
            required = []

        if not optional:
            optional = []

        keys = required + optional

        if not keys:
            raise ValueError('No parameters specified')

        for i in range(0, len(keys), 10):
            response = self._ssm.get_parameters(
                Names=[f'/{self._env}{key}' for key in keys[i:i+10]],
                WithDecryption=True
            )

            for param in response['Parameters']:
                name = param['Name'][len(self._env)+1:]
                params[name] = param['Value']

        missing_required = list(required - params.keys())
        if missing_required:
            raise SSMParameterStoreError(
                f'Required parameters not found in {self._env}: {missing_required}'
            )

        return params 