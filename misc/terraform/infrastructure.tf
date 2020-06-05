terraform {
  backend "s3" {
    bucket = "terraformstate.stochastic.io"
    key    = "spamnesty/terraform.tfstate"
    region = "eu-central-1"
  }
}

variable "cloudflare_email" {}
variable "cloudflare_token" {}
variable "zone_id" {
  default = "e43bf90424083ce1525ad8bf7d0f4661"
}

variable ipv6_ip { default = "2a01:4f8:1c0c:6109::1" }
variable ipv4_ip { default = "195.201.40.251" }
variable domain { default = "mnesty.com" }

provider "cloudflare" {
  version = "~> 2.0"
  email   = var.cloudflare_email
  api_key = var.cloudflare_token
}

resource "cloudflare_record" "root4" {
  zone_id = var.zone_id
  proxied = "true"
  type    = "A"
  name    = "@"
  value   = "${var.ipv4_ip}"
}

resource "cloudflare_record" "www4" {
  zone_id = var.zone_id
  proxied = "true"
  type    = "A"
  name    = "www"
  value   = "${var.ipv4_ip}"
}

resource "cloudflare_record" "spa4" {
  zone_id = var.zone_id
  proxied = "true"
  type    = "A"
  name    = "spa"
  value   = "${var.ipv4_ip}"
}

resource "cloudflare_record" "mail" {
  zone_id = var.zone_id
  proxied = "false"
  type    = "A"
  name    = "mail"
  value   = "78.47.150.26"
}

resource "cloudflare_record" "root6" {
  zone_id = var.zone_id
  proxied = "true"
  type    = "AAAA"
  name    = "@"
  value   = "${var.ipv6_ip}"
}

resource "cloudflare_record" "spa6" {
  zone_id = var.zone_id
  proxied = "true"
  type    = "AAAA"
  name    = "spa"
  value   = "${var.ipv6_ip}"
}

resource "cloudflare_record" "www6" {
  zone_id = var.zone_id
  proxied = "true"
  type    = "AAAA"
  name    = "www"
  value   = "${var.ipv6_ip}"
}

resource "cloudflare_record" "tracking" {
  zone_id = var.zone_id
  proxied = "false"
  type    = "CNAME"
  name    = "tracking"
  value   = "api.elasticemail.com"
}

resource "cloudflare_record" "email" {
  zone_id = var.zone_id
  proxied = "false"
  type    = "CNAME"
  name    = "email"
  value   = "mailgun.org"
}

resource "cloudflare_record" "mxw1" {
  zone_id  = var.zone_id
  proxied  = "false"
  type     = "MX"
  name     = "*"
  value    = "mail.mnesty.com"
  priority = "10"
}

resource "cloudflare_record" "mx1" {
  zone_id  = var.zone_id
  proxied  = "false"
  type     = "MX"
  name     = "@"
  value    = "mail.mnesty.com"
  priority = "10"
}

resource "cloudflare_record" "spf" {
  zone_id = var.zone_id
  proxied = "false"
  type    = "TXT"
  name    = "@"
  value   = "v=spf1 a mx include:_spf.elasticemail.com include:mailgun.org ~all"
}

resource "cloudflare_record" "dkim" {
  zone_id = var.zone_id
  proxied = "false"
  type    = "TXT"
  name    = "mailo._domainkey"
  value   = "k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDX16UZfYbYtEPC/4GgUkf7wGmLotT4Oh/I8QnmirMacjxqNQ+X+U7LY2VMC8wpeoTmv9a4H2GDqcCBoQsdDOTLu1NcN3DRBXrbDkndqQkwRW6vC8XhIXra2xyykKsOPUhuP4afNCcloV832tq4Y/BTGb5zqWeoBLi+BTDeYLh1lwIDAQAB"
}

resource "cloudflare_record" "dkim2" {
  zone_id = var.zone_id
  proxied = "false"
  type    = "TXT"
  name    = "api._domainkey"
  value   = "k=rsa;t=s;p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCbmGbQMzYeMvxwtNQoXN0waGYaciuKx8mtMh5czguT4EZlJXuCt6V+l56mmt3t68FEX5JJ0q4ijG71BGoFRkl87uJi7LrQt1ZZmZCvrEII0YO4mp8sDLXC8g1aUAoi8TJgxq2MJqCaMyj5kAm3Fdy2tzftPCV/lbdiJqmBnWKjtwIDAQAB"
}
