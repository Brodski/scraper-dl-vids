locals {
    website_name = ( var.ENV == "dev"  ? "dev-captions.bski.one" :
                     var.ENV == "prod" ? "www.twitchtranscripts.com" : "default_value" )
}