---
title: Azure Nibble - How to get TcpPing on Linux Azure App Service
published: false
description: Azure - Nibble - How to get TcpPing on Linux Azure App Service
tags: 'tutorial, azure, productivity, learning'
cover_image: assets/main-azure-nibble.png
canonical_url: null
id: 763498
---

## Ping vs. TcpPing?

**Ping** is a computer network administration software utility used to test the reachability of a host on an Internet Protocol (IP) network using Internet Control Message Protocol (ICMP).  

There can be instances where a remote host, has blocked ICMP traffic, which in turn means we cannot test/check to connectivity to the remote host. In this kind of a situation, what you can do to check the host's presence is to telnet to a known port or to try making a TCP connection to the host.  

This is where **tcpping** comes in and is a TCP oriented **ping** alternative. It is used to test the reachability of a service on a host using TCP/IP and measure the time it takes to connect to the specified port. It is a very useful tool to help with diagnosing network related issues on Azure App Service.

Windows based app services in Azure automatically have **tcpping** enabled, however this valuable tool is missing on linux based app services, so in todays tutorial we will look at how we can get and run **tcpping** on linux based app services.

## Installation

1. Go to your Kudu site (i.e https://<sitename>.scm.azurewebsites.net/webssh/host) to SSH into your app.
2. apt-get install tcptraceroute
3. cd /usr/bin
4. wget http://www.vdberg.org/~richard/tcpping
5. chmod 755 tcpping
6. apt install bc

## How to use

tcpping [-d] [-c] [-r sec] [-x count] ipaddress [port]  

- -d: print timestamp before each result.
- -c: use columned output for easy parsing.
- -r: interval in seconds between consecutive probes (1 second by default).
- -x: repeat n times (unlimited by default).
- [port]: target port (80 by default).

