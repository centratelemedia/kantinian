#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PyFingerprint
Copyright (C) 2015 Bastian Raschke <bastian.raschke@posteo.de>
All rights reserved.

"""

import tempfile, sys, os, time, json, requests
from pyfingerprint.pyfingerprint import PyFingerprint

port = '/dev/ttyS0'
minQ = 100
urlServer = 'http://13.67.75.133/absensi/api/finger.php'

try:
    f = PyFingerprint(port, 57600, 0xFFFFFFFF, 0x00000000)
    if ( f.verifyPassword() == False ):
        raise ValueError('The given fingerprint sensor password is wrong!')

    print('Currently used templates: ' + str(f.getTemplateCount()) +'/'+ str(f.getStorageCapacity()))

except Exception as ex:
    print(ex)
    exit()

def getImage():
    ## Tries to read image and download it
    try:
        print('Waiting for finger...')

        ## Wait that finger is read
        while ( f.readImage() == False ):
            time.sleep(.1)
            pass

        print('Downloading image (this take a while)...')

        imageDestination =  os.getcwd() + '/fingerprint.bmp'
        f.downloadImage(imageDestination)

        print('The image was saved to "' + imageDestination + '".')
        return imageDestination

    except Exception as e:
        print('Operation failed!')
        print('Exception message: ' + str(e))
        exit(1)

def enroll(nim = f.getTemplateCount()):
    ''' enrolling new user, and return characteristic '''
    try:
        newHeaders = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        response = requests.get(urlServer, json={
            'mode': 'getid',
            'nim': nim,
            },headers=newHeaders, verify=False)
        response_json = json.loads(response.text)
        
        if(response_json['status'] == 'fail'):
            return False

        id = response_json['data']
        
        print('Waiting for finger...')
        while( f.readImage() == False ):
            time.sleep(.1)
            pass

        print('Convert image to charbuffer1')
        f.convertImage(0x01)

        print('Remove finger')
        while(f.readImage() == True):
            time.sleep(.1)
            pass

        print('Place same finger')
        while(f.readImage() == False):
            time.sleep(.1)
            pass

        print('Convert image to charbuffer2')
        f.convertImage(0x02)
        
        s = f.compareCharacteristics()
        if(int(s) < minQ):
            raise ValueError('Finger not same')
        
        print('Create template')
        f.createTemplate()

        c = f.downloadCharacteristics()
        s = ','.join([str(e) for e in c]).strip()
        
        newHeaders = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        response = requests.get(urlServer, json={
            'mode': 'enroll',
            'id_user': id,
            'finger_char': s
            },headers=newHeaders, verify=False)
        print(response.text)
    
        response_json = json.loads(response.text)
        if(response_json['status'] == 'success'):
            print('true')
            return True
        else:
            print('false')
            return False
        
    except Exception as ex:
        print(ex)


def loadFromDatabase():
    try:
        newHeaders = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        response = requests.get(urlServer, json={'mode': 'request'},headers=newHeaders, verify=False)
        response_Json = json.loads(response.text)
        f.clearDatabase()
        for data in response_Json['data']:
            c = list(map(int, data['finger_char'].split(',')))
            id = data['id_user']

            if(len(c) < 512):
                print('Finger char for id: ', id, ' Error')
                continue
            if(int(id) > 999):
                print('Finger id over the maximum number')
                continue
            f.uploadCharacteristics(characteristicsData=c)
            f.storeTemplate(positionNumber=int(id))
            print('Berhasil mendaftarkan id: ',id)

        return True;
    except Exception as ex:
        print(ex)
        return False;

def searchFinger():
    try:
        while(f.readImage() == False):
            time.sleep(.1)
            pass
        f.convertImage()
        [p,q] = f.searchTemplate()
        print(p, " quality: ", q)

        if(p < 0):
            raise ValueError('Finger not found')

        if(q < minQ):
            raise ValueError('Finger not match')
            
        print('Found: ',p,' quality: ', q)
        return [p, q]
    except Exception as ex:
        return [-1, -1];
        print(ex)

#loadFromDatabase()
#searchFinger()
##enroll('123')
