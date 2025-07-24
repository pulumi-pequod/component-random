# component-random
A simple component that uses the random provider. 
It is here mostly for testing and simple demonstration use-cases. 

## Release Workflow
* Make your changes and test them.
* Create a PR and merge it to main.
* Create a new release tag:
  ```sh
  git tag vX.Y.Z
  git push origin tag vX.Y.Z
  ```
* This should trigger a github action that:
  * Publishes the new version of component to the org. (work in progress)
  * Updates the component version in the component version check policy. (stretch goal)
