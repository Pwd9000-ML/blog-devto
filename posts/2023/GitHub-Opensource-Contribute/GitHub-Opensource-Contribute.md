---
title: Open Source Contribution on GitHub
published: false
description: Understanding Open Source Contribution on GitHub
tags: 'github, developer, opensource, devops'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2023/GitHub-Opensource-Contribute/assets/main-gh-tips.png'
canonical_url: null
id: 1588134
series: GitHub Pro Tips
---

## Demystifying Your First Open Source Contribution

Open source projects have made a profound impact on the world of software development. They foster a collaborative ecosystem that encourages code sharing, mutual learning, and technological advances at an unprecedented pace.  

As a developer, contributing to open source projects on **GitHub** can boost your skills, broaden your network, and amp up your resume. Despite these advantages, contributing to an open source community for the first time can feel daunting.  

Hopefully this post will server as a comprehensive guide that walks you through finding suitable open source projects, understanding their contribution guidelines, and making your first pull request on **GitHub**.  

## Discovering Open Source Projects

Firs look at finding a suitable project, one that aligns with your skills, interests, and the tech stack you're familiar with or wish to learn. Here are some tips to help you find the right project:

**[GitHub Explore:](https://github.com/explore)** This is a built-in feature on GitHub that lets you explore popular repositories, trending developers, topic-wise collections, and other curated sections. This wealth of content is a great starting point to discover open-source projects that match your abilities and interests.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2023/GitHub-Opensource-Contribute/assets/explore.png)

**[Awesome Lists:](https://github.com/topics/awesome)** Awesome Lists are meticulously curated compilations which span across many GitHub Repositories and topics, such as ***"Awesome Python"***, ***"Awesome Machine Learning"***, or ***"Awesome Docker"***. These lists include a myriad of superbly crafted libraries and tools worthy of your attention, and potential contribution.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2023/GitHub-Opensource-Contribute/assets/awesome.png)

**GitHub Search:** Use GitHub's advanced search feature to seek out projects using specific filters, such as repositories written in a particular language, those with issues flavored as ***'good first issue'*** or ***'help wanted'***, or projects that have not been updated recently.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2023/GitHub-Opensource-Contribute/assets/search.png)

## Contributing Guidelines

An essential step before making any contribution is to review the project's contribution guidelines, which will guide you throughout your contribution journey. These guidelines are typically found in a file named `CONTRIBUTING.md`, `CONTRIBUTING.md`, or `HOW_TO_CONTRIBUTE.md` in the project repository. In some cases, it might also be a part of the `README.md` file.

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2023/GitHub-Opensource-Contribute/assets/cont.png)

**The guidelines may contain:**

1. **Code of Conduct:** This outlines the expectations for participation in the community, as well as the consequences for unacceptable behavior.

2. **What to Contribute:** Most projects clarify what they expect from contributors, be it bug reports, feature requests, or code improvements.

3. **Pull Request Process:** Step-by-step guidance on how to submit a pull request (PR) for the project.

4. **Coding Standards:** The coding conventions, like code styling and testing procedures, used in the project.

If the contributing guidelines seem unclear, do not hesitate to open an issue asking the maintainers for clarification.

## Making Your First Pull Request

Finally, let's focus on the most rewarding part, contributing to an open-source project by making a pull request.  
Here are the steps to follow:

**Fork the Repository:** GitHub allows users to create a personal copy of another user's project. This is known as forking a repository. Find the `'Fork'` button located at the top-right corner of the project page and click on it. Within a few seconds, a copy of the repository will appear in your account.

![image.png]()

**Clone the Repository:** The next step is to get this remote repository on your local system for making changes. This is known as `'cloning'`. Use the git clone command followed by the URL of your forked repository.

![image.png]()

**Create a New Branch:** It's a good practice to create a new branch for each new feature or bug fix you work on, to keep your contributions organized. Use the git branch `'branch_name'` to create a new branch, and git checkout branch_name to switch to it.

![image.png]()

**Make Changes and Commit:** Now, dive into the code. First, open the code in your preferred Integrated Development Environment (IDE), such as [VSCode]() or even a [GitHub Codespace]() . Make the necessary changes and save them. After making changes, use `git add .` to stage the changes, and `git commit -m "commit message"` to save your changes. Be sure to write a meaningful commit message, explaining the changes you made.

![image.png]()

**Push Your Changes:** After committing your changes, it's time to upload them to your **forked repository** on GitHub. This process is known as `'pushing'`. The `git push origin your_branch_name` command will push your changes to your forked GitHub repository.

![image.png]()

**Create a Pull Request:** Navigate back to your forked repository on GitHub. Click on `'Pull Request'` then create a new pull request. Ensure the source branch is **your** recently created **branch** and the destination branch is the master branch of the original repository. Summarize the changes you've made, then click `'Create a pull request'`.

![image.png]()

Pat yourself on the back! You've just made your first pull request. The maintainers of the original repository will then review your request, provide feedback or suggest changes (if required), and finally merge the changes into the original repository.

## Conclusion

Venturing into the world of open source contributions can seem like an uphill task, particularly if you are just getting started. However, with a resource like GitHub at your disposal, and with these steps in mind, the process becomes significantly more manageable and less intimidating.

Remember, contributing to open source projects extends far beyond bug fixes or feature additions. It involves learning and growing, enhancing your coding skills, understanding and participating in the dynamics of software development workflow, and above all, becoming a part of a community— all while contributing to the code that runs the world.

So, find a project that resonates with your interest, understand its guidelines, and make your first pull request. Every contribution, no matter how small, matters. The world of open source is waiting for what you have to offer. Happy coding!

I hope you have enjoyed this post and have learned something new. :heart:

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [Twitter](https://twitter.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
