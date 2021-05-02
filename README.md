# Usage

## Build Status

[![Build Status](https://github.com/Pwd9000-ML/blog-devto/workflows/publish-to-devto/badge.svg)](https://github.com/Pwd9000-ML/blog-devto/actions)

## How to

## How to find the ID of my blog post on dev.to?

This repository is made to **edit** a blog post. Whether it's published or just a draft, you **have to create it** on dev.to directly. Unfortunately, dev.to does not display the ID of the blog post on the page. So once it's created, you can open your browser console and paste the following code to retrieve the blog post ID:  
`$('div[data-article-id]').getAttribute('data-article-id')`
