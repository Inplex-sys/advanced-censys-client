################################################################################
#                          Copyrights and license                              #
################################################################################
#                                                                              #
# Copyright 2021 Inplex-sys <Inplex-sys@protonmail.com>                        #
#                                                                              #
# This file is part of Dark Utilities.                                         #
# https://dark-utilities.me/                                                   #
#                                                                              #
# Dark Utilities is paying software: you can redistribute it and/or modify it  #
# under the terms of the GNU Lesser General Public License as published by the #
# Free Software Foundation, either version 3 of the License, or                #
# (at your option)  any later version.                                         #
#                                                                              #
# Dark Utilities is distributed in the hope that it will be useful, but        #
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY   #
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public       #
# License for more details.                                                    #
#                                                                              #
# You should Dark Utilities received a copy of the GNU Lesser General Public   #
# License                                                                      #
# along with Dark Utilities. If not, see <http://www.gnu.org/licenses/>.       #
#                                                                              #
################################################################################
#                     Made with ❤️ by github.com/inplex-sys                    #
################################################################################

import requests
import string
import colored
import random
import sys, os
import time
import argparse

class Main:
    def genString( length ):
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))
        pass
    
    def textHighlight( text ):
        return colored.stylize(text, colored.fg('wheat_1'), colored.attr('bold'))
        pass
    
    def textSuccess( text ):
        return colored.stylize(text, colored.fg('green'))
        pass

    def textDanger( text ):
        return colored.stylize(text, colored.fg('red'))
        pass
    
    def textPrimary( text ):
        return colored.stylize(text, colored.fg('cyan'))
        pass

class Setup:
    def help():
        print(f"\n{Main.textHighlight('Usage:')} python3 {sys.argv[0]} query [options]")
        print(f"    {Main.textHighlight('Options:')}")
        print(f"        {Main.textPrimary('--help')} : Show this help")
        print(f"        {Main.textPrimary('--config')} : Configure API ID and API Secret\n")
        pass

    def getConfig():
        auths = []
        with open('config.txt', 'r') as file:
            lines = file.read().splitlines()
            for line in lines:
                auths.append((line.split(':')[0], line.split(':')[1]))
                pass
            file.close()
            pass

        return auths
        pass

    def config():
        username = str(input(f"Censys API ID {Main.textPrimary('(********************************98d1)')}: "))
        password = str(input(f"Censys API Secret {Main.textPrimary('(****************************aucc)')}: "))
        
        if username == '' or password == '':
            print(f"You have provided {Main.textDanger('unvalid')} Censys API ID and API Secret")
            addOther = str(input("Would you like to retry ? (y/n): "))
            if addOther == 'y':
                os.system('cls' if os.name == 'nt' else 'clear')
                Setup.config()
            else:
                return False
                pass
            pass

        with open('./config.txt', 'a+') as file:
            lines = file.readlines()
            for line in lines:
                if username == line.split(':')[0]:
                    print("API ID and API Secret already set")
                    addOther = str(input("Would you like to retry ? (y/n): "))
                    if addOther == 'y':
                        os.system('cls' if os.name == 'nt' else 'clear')
                        Setup.config()
                    else:
                        return False
                        pass
                    pass
                pass
            pass

            if Censys.check( username, password ):
                file.write(f"{username}:{password}\n")
            else:
                print(f"This API ID and API Secret are {Main.textDanger('not registered')}")
                addOther = str(input("Would you like to retry ? (y/n): "))
                if addOther == 'y':
                    os.system('cls' if os.name == 'nt' else 'clear')
                    Setup.config()
                else:
                    return False
                    pass
                pass
                
            file.close()
            pass
            
        print(f"Your API ID and API Secret have been {Main.textSuccess('successfully')} saved to {Main.textHighlight('config.txt')}")
        addOther = str(input("Would you like to add another API ID and API Secret ? (y/n): "))
        if addOther == 'y':
            os.system('cls' if os.name == 'nt' else 'clear')
            Setup.config()
        else:
            return False
            pass
        pass

class Censys:
    def __init__( self, auth, output ):
        self.auth = auth
        self.totalAuth = len(auth)
        self.rawData = ''

        self.headers = {
            'Accept': 'application/json',
            'User-Agent': 'censys-api-client-python/1.0.0'
        }

        if output != None: 
            self.outputFile = output
        else: 
            self.outputFile = f'./result-{Main.genString(10)}.txt'
            pass

        self.quota = self.account()['quota']
        pass

    @staticmethod
    def check( username, password ):
        httpResponse = requests.get('https://search.censys.io/api/v1/account', headers={'Accept': 'application/json'}, auth=(username, password))
        if httpResponse.status_code == 200:
            return True
        else:
            return False
            pass
        pass

    def account( self, auth=False ):
        if not auth:
            httpResponse = {
                'quota': {
                    'used': 0,
                    'allowance': 0,
                }
            }

            for user, password in self.auth:
                response = requests.get('https://search.censys.io/api/v1/account', headers=self.headers, auth=(user, password)).json()
                if 'error' not in response.keys():
                    httpResponse['quota']['used'] += response['quota']['used']
                    httpResponse['quota']['allowance'] += response['quota']['allowance']
                    pass
                pass
            pass
        else:
            httpResponse = requests.get('https://search.censys.io/api/v1/account', headers=self.headers, auth=auth).json()
            pass
        return httpResponse
        pass

    def count( self, query ):
        httpQuery = '?q=%s&per_page=100' % query

        try:
            httpResponse = requests.get('https://search.censys.io/api/v2/hosts/search' + httpQuery, headers=self.headers, auth=self.auth[0]).json()

            if httpResponse['code'] == 429:
                print(f"The quota has been reached for {Main.textHighlight(self.auth[0][0])}, there is {Main.textHighlight(str(len(self.auth)-1)) + '/' + Main.textHighlight(str(self.totalAuth))} auths left, switching ...")
                del self.auth[0]
                return self.count(query)
                pass

            if httpResponse['code'] == 200:
                return httpResponse['result']['total']
                pass
        except:
            time.sleep(1)
            return self.count(query)
            pass 
        pass

    def search( self, query, cursor=False ):
        httpQuery = '?q=%s&per_page=100' % (query) if not cursor else '?q=%s&per_page=100&cursor=%s' % (query, cursor)

        try:
            httpResponse = requests.get('https://search.censys.io/api/v2/hosts/search' + httpQuery, headers=self.headers, auth=self.auth[0]).json()
            if httpResponse['code'] == 429:
                print(f"The quota has been reached for {Main.textHighlight(self.auth[0][0])}, there is {Main.textHighlight(str(len(self.auth)-1)) + '/' + Main.textHighlight(str(self.totalAuth))} auths left, switching ...")
                del self.auth[0]
                pass

            with open(self.outputFile, 'a+') as file:
                for result in httpResponse['result']['hits']:
                    self.rawData += f'{result["ip"]}\n'
                    print(f"{Main.textHighlight(len(self.rawData.splitlines()))} results found ...", end='\r')
                    file.write(f'{result["ip"]}\n')
                    pass
                file.close()
                pass

            if len(self.auth) == 0:
                print(f'No more auths usable, all data have been saved in {Main.textHighlight(self.tempFile)}')
                exit()
                pass

            if httpResponse['result']['links']['next'] == '':
                print(f'All data have been saved in {Main.textHighlight(self.tempFile)}')
                pass

            if httpResponse['code'] == 200:
                time.sleep(1)
                self.search(query, httpResponse['result']['links']['next'])
                pass
        except:
            time.sleep(1)
            self.search(query, cursor)
            pass
        pass

def main():
    if "--config" in sys.argv:
        Setup.config()
        return False
    elif "--help" in sys.argv:
        Setup.help()
        return False
        pass

    if len(sys.argv) < 2:
        Setup.help()
        return False
        pass

    if len(sys.argv) < 3:
        file = None
    else:
        file = sys.argv[2]
        pass

    censys = Censys( Setup.getConfig(), file)

    print(f"There is {Main.textHighlight(len(censys.auth))} accounts loaded for {Main.textHighlight(str(censys.quota['used']) + '/' + str(censys.quota['allowance']))} queries usable.")
    print(f"All data are going to be saved in {Main.textHighlight(censys.outputFile)}\n")

    totalCount = censys.count( sys.argv[1] )
    print(f"{Main.textHighlight(totalCount)} results found ...")

    print(f"Searching for {Main.textHighlight(sys.argv[1])} ...")
    censys.search( sys.argv[1] )
    pass

if __name__ == '__main__':
    main()
