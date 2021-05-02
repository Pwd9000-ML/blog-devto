# Devto - Blog - Status

## Build Status

[![publish to Dev.to](https://github.com/Pwd9000-ML/blog-devto/actions/workflows/publish-to-devto.yml/badge.svg)](https://github.com/Pwd9000-ML/blog-devto/actions/workflows/publish-to-devto.yml)

## How to

### How to find the ID of my blog post on dev.to?

This repository is made to **edit** a blog post. Whether it's published or just a draft, you **have to create it** on dev.to directly. Unfortunately, dev.to does not display the ID of the blog post on the page. So once it's created, you can open your browser console and paste the following code to retrieve the blog post ID:  
`$('div[data-article-id]').getAttribute('data-article-id')`

### How to test locally in yarn?

- Install Yarn and navigate to repo root. Run `Yarn` to download `node_modules` and dependencies described in `package.json`. This also updates and creates `yarn.lock`

- `package.json` also contains scripts that can then be manually run locally for `prettier` and `embedme`. These wun automatically in the Github Action as well when a post is published.
