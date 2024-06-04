locals {
    website_name = ( var.ENV == "dev"  ? "dev-mini.bski.one" :
                     var.ENV == "prod" ? "mini.bski.one" : "default_value" )
}