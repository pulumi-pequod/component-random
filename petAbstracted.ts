import * as pulumi from "@pulumi/pulumi";
import * as random from "@pulumi/random";

export interface PetAbstractedArgs {
    /**
     * The size of the pet name to generate. Valid values are "small", "medium", "large", "xlarge", or a number representing the length of the pet name.
     **/
    size: string;
}

// This resource abstracts using the RandomPet resource to generate a pet name based on a size parameter.
export class PetAbstracted extends pulumi.ComponentResource {
    /**
     * The generated pet name.
     **/
    public readonly petName: pulumi.Output<string>;

    constructor(name: string, args: PetAbstractedArgs, opts?: pulumi.ComponentResourceOptions) {
        super("random-abstracted:index:PetAbstracted", name, args, opts);

        const size = args.size || "small";

        var petNameLength: number;
        switch (size) {
            case "small":
                petNameLength = 2;
                break;
            case "medium":
                petNameLength = 4;
                break;
            case "large":
                petNameLength = 6;
                break;
            case "xlarge":
                petNameLength = 8;
                break;
            default:
                petNameLength = Number(size);
                if (isNaN(petNameLength)) {
                    throw new Error(`Invalid size: "${size}". Must be "small", "medium", "large" or "xlarge" or a number.`);
                }
        }

        const petName = new random.RandomPet("petName", {
            length: petNameLength,
        }, { parent: this });

        this.petName = petName.id

        this.registerOutputs({});

    }
}