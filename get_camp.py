#!/usr/bin/env python
#
# Copyright 2016 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This example gets all campaigns.
To add a campaign, run add_campaign.py.
The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.
"""


from googleads import adwords


PAGE_SIZE = 100


def main(client):
  # Initialize appropriate service.
  campaign_service = client.GetService('TargetingIdeaService', version='v201809')

  # Construct selector and get all campaigns.
  
  selector = {
      'ideaType': 'KEYWORDS',
      'requestType': 'STATS'
  }

  selector['requestedAttributeTypes'] = [
    'KEYWORD_TEXT', 'SEARCH_VOLUME', 'CATEGORY_PRODUCTS_AND_SERVICES']

  offset = 0
  selector['paging'] = {
    'startIndex': str(offset),
    'numberResults': str(PAGE_SIZE)
  }

  selector['searchParameters'] = [{
    'xsi_type': 'RelatedToQuerySearchParameter',
    'queries': ['space']
  }]

  

  

  more_pages = True
  page = campaign_service.get(selector)

    # Display results.
  for result in page['entries']:
    attributes = {}
    for attribute in result['data']:
      attributes[attribute['key']] = getattr(
        attribute['value'], 'value', '0')
      print('Keyword with "%s" text and average monthly search volume '
        '"%s" was found with Products and Services categories: %s.'
        % (attributes['KEYWORD_TEXT'],
          attributes['SEARCH_VOLUME'],
          attributes['CATEGORY_PRODUCTS_AND_SERVICES']))
  offset += PAGE_SIZE
  
  more_pages = offset < int(page['totalNumEntries'])


if __name__ == '__main__':
  adwords_client = adwords.AdWordsClient.LoadFromStorage("googleads.yaml")
  main(adwords_client)