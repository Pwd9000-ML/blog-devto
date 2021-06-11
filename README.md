# Devto - Blog - Status

## How to

### How to find the ID of a blog post on dev.to?

Unfortunately, dev.to does not display the ID of the blog post on the page. So once it's created, you can open your browser console (Usually F12) and paste the following code to retrieve the blog post ID:  
`$('div[data-article-id]').getAttribute('data-article-id')`  
If anyone knows of an easier way please help by submitting a PR here. :smile:

### How to test locally with yarn?

- Install Yarn and navigate to the repo root. Run `Yarn` to download `node_modules` and dependencies described in `package.json`. This will also update / create `yarn.lock`

- `package.json` also contains some scripts that can then be run locally for `prettier` and `embedme`. Also used in the Github Action when a post is published.
