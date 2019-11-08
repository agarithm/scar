# Copyright (C) GRyCAP - I3M - UPV
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Module with classes and methods that manage the AWS ApiGateway at high level."""

from typing import Dict
from scar.providers.aws import GenericClient
import scar.logger as logger

class APIGateway(GenericClient):
    """Manage the calls to the ApiGateway client."""

    def __init__(self, aws_properties: Dict):
        super().__init__(aws_properties.get('api_gateway', {}))
        self.aws = aws_properties
        self.api = self.aws_properties.get('api_gateway', {})

    def _get_common_args(self) -> Dict:
        return {'restApiId' : self.api.get('id', ''),
                'resourceId' : self.api.get('resource_id', ''),
                'httpMethod' : self.api.get('http_method', '')}

    def _get_method_args(self) -> Dict:
        return self._get_common_args().update(self.api.get('method', {}))

    def _get_integration_args(self) -> Dict:
        integration_args = self.api.get('integration', {})
        uri_args = {'api_region': self.api.get('region', ''),
                    'lambda_region': self.aws.get('lambda', {}).get('region', ''),
                    'account_id': self.aws.get('iam', {}).get('account_id', ''),
                    'function_name': self.aws.get('lambda', {}).get('name', '')}
        integration_args['uri'] = integration_args['uri'].format(**uri_args)
        return self._get_common_args().update(integration_args)

    def _get_resource_id(self) -> str:
        res_id = ""
        resources_info = self.client.get_resources(self.api.get('id',''))
        for resource in resources_info['items']:
            if resource['path'] == '/':
                res_id = resource['id']
                break
        return res_id

    def _set_api_gateway_id(self, api_info: Dict) -> None:
        self.api['id'] = api_info.get('id', '')
        
    def _set_resource_info_id(self, resource_info: Dict) -> None:
        self.api['resource_id'] = resource_info.get('id', '')        

    def _get_endpoint(self) -> str:
        endpoint_args = {'api_id': self.api.get('id',''), 'api_region': self.api.get('region','')}
        return self.api.get('endpoint','').format(**endpoint_args)

    def create_api_gateway(self) -> None:
        """Creates an Api Gateway endpoint."""
        api_info = self.client.create_rest_api(self.api.get('name',''))
        self._set_api_gateway_id(api_info)
        resource_info = self.client.create_resource(self.api.get('id',''),
                                                    self._get_resource_id(),
                                                    self.api.get('path_part', ''))
        self._set_resource_info_id(resource_info)
        self.client.create_method(**self._get_method_args())
        self.client.set_integration(**self._get_integration_args())
        self.client.create_deployment(self.api.get('id',''), self.api.get('stage_name', ''))
        logger.info(f'API Gateway endpoint: {self._get_endpoint()}')

    def delete_api_gateway(self, api_gateway_id: str) -> None:
        """Deletes an Api Gateway endpoint."""
        return self.client.delete_rest_api(api_gateway_id)
