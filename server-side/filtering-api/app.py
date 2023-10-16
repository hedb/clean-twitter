#!/usr/bin/env python3

from aws_cdk import core

from cdk.filteringapistack import FilteringAPIStack  # Importing the stack class from your module

app = core.App()
FilteringAPIStack(app, "FilteringAPIStack")  # Initializing your stack

app.synth()  # Synthesizes an AWS CloudFormation template for the defined app
