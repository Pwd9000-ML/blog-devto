---
title: Azure Nibble - How to get TcpPing on Linux Azure App Service
published: true
description: Azure - Nibble - How to get TcpPing on Linux Azure App Service
tags: 'azureappservice, azure, appservices, webapps'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021/Azure-Nibble-TcpPing-Linux-Appsvc/assets/main-azure-nibble.png'
canonical_url: null
id: 763498
date: '2021-07-19T16:34:17Z'
---

## Ping vs. TcpPing?

**Ping** is a computer network administration software utility used to test the reachability of a host on an Internet Protocol (IP) network using Internet Control Message Protocol (ICMP).

There can be instances where a remote host, has blocked ICMP traffic, which in turn means we cannot test/check the connectivity to the remote host. In this kind of a situation, what you can do to check the host's presence is to telnet to a known port or to try making a TCP connection to the host.

This is where **tcpping** comes in and is a TCP oriented **ping** alternative. It is used to test the reachability of a service on a host using TCP/IP and measure the time it takes to connect to the specified port. It is a very useful tool to help with diagnosing network related issues on Azure App Service.

Windows based app services in Azure automatically have **tcpping** enabled, however this valuable tool is missing on linux based app services, so in todays tutorial we will look at how we can get and run **tcpping** on linux based app services.

## Installation

Go to your app service Kudu site: **<https://[sitename].scm.azurewebsites.net/webssh/host>** to establish a SSH web session. Or use the azure portal to navigate to the kudu site as follow:

![aznav](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021/Azure-Nibble-TcpPing-Linux-Appsvc/assets/aznav.png)

![kudu2](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021/Azure-Nibble-TcpPing-Linux-Appsvc/assets/kudu2.png)

Run the following:

1. `apt-get install tcptraceroute` (**Required:** if not already present.)
2. `apt-get install bc` (**Required:** if minimal Linux Runtime used, e.g. docker.)
3. `cd /usr/bin`
4. `wget http://www.vdberg.org/~richard/tcpping`
5. `chmod 755 tcpping`

## How to use

`tcpping [-d] [-c] [-r sec] [-x count] ipaddress [port]`

- [-d]: print timestamp before each result.
- [-c]: use columned output for easy parsing.
- [-r]: interval in seconds between consecutive probes (1 second by default).
- [-x]: repeat n times (unlimited by default).
- [port]: target port (80 by default).

![tcpping1](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2021/Azure-Nibble-TcpPing-Linux-Appsvc/assets/tcpping1.png)

I hope you have enjoyed this post and have learned something new. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
