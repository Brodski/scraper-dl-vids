locals {
    website_name = ( var.ENV == "dev"  ? "dev-captions.bski.one" :
                     var.ENV == "prod" ? "donkey" : "default_value" )
    # image_uri = "144262561154.dkr.ecr.us-east-1.amazonaws.com/idontfront:official_v2.1"
    # image_uri = "144262561154.dkr.ecr.us-east-1.amazonaws.com/idontfront:official_v2"
}