# component-random
Pulumi component that provides an abstraction for the Random provider's `petName` resource.

# Usage
## Specify Package in `Pulumi.yaml`

Add the following to your `Pulumi.yaml` file:
Note: If no version is specified, the latest version will be used.

```
packages:
  component-random: https://github.com/pulumi-pequod/component-random[@vX.Y.Z]
``` 

## Use SDK in Program

### Python
```
from pulumi_pequod_random_abstracted import PetAbstracted

pet_name = PetAbstracted("my-petname", 
                        size="medium")
```

### Typescript
```
import { PetAbstracted } from "@pulumi-pequod/random-abstracted";

const petName = new PetAbstracted(baseName, { size: "large" })
```

### Dotnet
```
using PulumiPequod.RandomAbstracted;

var petName = new PetAbstracted("myPetName");
```

### YAML
```
  petName:
    type: random-abstracted:PetAbstracted
    properties:
      size: ${size}
```










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
