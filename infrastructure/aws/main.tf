provider "aws" {
    region = "us-east-1"
}

# Baseline Launch Template constraint for the Architect to inspect
resource "aws_launch_template" "compute_node" {
    name = "agent-os-compute-node"
    instance_type = "m5.large"
}
