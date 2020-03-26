# Contributor's Guide
Welcome and thank you for your interest in contributing to the this open source project. This documentation aims to document how contributors and collaborators should work when using Git, GitHub and the development workflow. This Git workflow is inspired greatly by the [QuantConnect Lean Contributors Guide](https://github.com/QuantConnect/Lean/blob/master/CONTRIBUTING.md).

## Style Guide
The project was written following [Google Python Style Guide](https://github.com/google/styleguide/blob/gh-pages/pyguide.md) and reviewers will be expecting to see code that follow it as well. But you should to use `black` instread of obsolete `yapf`. Please make sure, that your linter (pylint) and formatter (black) are using configs form repo's root.

## Testing
All pull requests must be accompanied by units tests. If it is a new feature, the tests should highlight expected use cases as well as edge cases, if applicable. If it is a bugfix, there should be tests that expose the bug in question.

## Brunching Strategy
The project following [GitLab Flow](https://docs.gitlab.com/ee/topics/gitlab_flow.html) strategy according to which:
- `master` is the primary brunch
- feature-brunches must branch off from `master`
- feature-brunches must be merged back into `master`

## Pull Requests
When you going to develop new feature or make some changes that will change the existing code, please create an issue to suggest changes. In other cases (bugfix, doc improvement and so on) you can just create pull request.

### Work In Progress
You can use `WIP` prefix in PR's name if you wish to get immediate feedback, but in this case you should take care of readability of your work-in-progress code. Thus please push changes only when you have a working set of tests and code.

Good lack!
