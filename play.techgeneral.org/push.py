#!/usr/bin/env python

import hashlib
import mimetypes
import os

import boto3

class Config(object):
    pass

def read_config():
    lines = [l.strip() for l in open(".awscredentials")]
    config = Config()
    config.access_key, config.secret_key, config.region_name, config.bucket_name, config.path = lines
    return config

def get_session(config):
    return boto3.Session(
        aws_access_key_id=config.access_key,
        aws_secret_access_key=config.secret_key,
        region_name=config.region_name,
    )

def main():
    config = read_config()
    session = get_session(config)
    s3 = session.resource('s3')
    bucket = s3.Bucket(config.bucket_name)
    objects = {}
    for object_summary in bucket.objects.filter(Prefix=config.path):
        objects[object_summary.key] = object_summary
    os.chdir("build")
    for root, dirs, files in os.walk("."):
        for name in files:
            filepath = os.path.join(root, name)
            if config.path:
                key = "%s/%s" % (config.path, filepath.replace('\\', '/').replace("./", ""))
            else:
                key = filepath.replace('\\', '/').replace("./", "")
            filecontents = open(filepath).read()
            existing_md5 = hashlib.md5(filecontents).hexdigest()
            if key in objects:
                obj = objects[key]
                if existing_md5 in obj.e_tag:
                    continue

            content_type, encoding = mimetypes.guess_type(filepath)
            bucket.put_object(
                Key=key,
                ACL="public-read",
                Body=filecontents,
                ContentLength=len(filecontents),
                ContentType=content_type,
            )

if __name__ == "__main__":
    main()
