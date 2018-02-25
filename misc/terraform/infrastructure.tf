terraform {
  backend "s3" {
    bucket = "terraformstate.stochastic.io"
    key    = "spamnesty/terraform.tfstate"
    region = "eu-central-1"
  }
}

variable "cloudflare_email" {}
variable "cloudflare_token" {}

provider "cloudflare" {
  email = "${var.cloudflare_email}"
  token = "${var.cloudflare_token}"
}

variable ipv6_ip { default = "2001:19f0:5:fc8:5400:ff:fe7d:1191" }
variable ipv4_ip { default = "45.63.15.100" }
variable domain { default = "mnesty.com" }

resource "cloudflare_record" "root4" {
    domain = "${var.domain}"
    proxied = "true"
    type = "A"
    name = "@"
    value = "${var.ipv4_ip}"
}

resource "cloudflare_record" "www4" {
    domain = "${var.domain}"
    proxied = "true"
    type = "A"
    name = "www"
    value = "${var.ipv4_ip}"
}

resource "cloudflare_record" "spa4" {
    domain = "${var.domain}"
    proxied = "true"
    type = "A"
    name = "spa"
    value = "${var.ipv4_ip}"
}

resource "cloudflare_record" "root6" {
    domain = "${var.domain}"
    proxied = "true"
    type = "AAAA"
    name = "@"
    value = "${var.ipv6_ip}"
}

resource "cloudflare_record" "spa6" {
    domain = "${var.domain}"
    proxied = "true"
    type = "AAAA"
    name = "spa"
    value = "${var.ipv6_ip}"
}

resource "cloudflare_record" "www6" {
    domain = "${var.domain}"
    proxied = "true"
    type = "AAAA"
    name = "www"
    value = "${var.ipv6_ip}"
}

resource "cloudflare_record" "email" {
    domain = "${var.domain}"
    proxied = "false"
    type = "CNAME"
    name = "email"
    value = "mailgun.org"
}

resource "cloudflare_record" "mxw1" {
    domain = "${var.domain}"
    proxied = "false"
    type = "MX"
    name = "*"
    value = "mxa.mailgun.org"
    priority = "10"
}

resource "cloudflare_record" "mxw2" {
    domain = "${var.domain}"
    proxied = "false"
    type = "MX"
    name = "*"
    value = "mxb.mailgun.org"
    priority = "20"
}

resource "cloudflare_record" "mx1" {
    domain = "${var.domain}"
    proxied = "false"
    type = "MX"
    name = "@"
    value = "mxa.mailgun.org"
    priority = "10"
}

resource "cloudflare_record" "mx2" {
    domain = "${var.domain}"
    proxied = "false"
    type = "MX"
    name = "@"
    value = "mxb.mailgun.org"
    priority = "20"
}

resource "cloudflare_record" "spf" {
    domain = "${var.domain}"
    proxied = "false"
    type = "TXT"
    name = "@"
    value = "v=spf1 include:mailgun.org ~all"
}

resource "cloudflare_record" "dkim" {
    domain = "${var.domain}"
    proxied = "false"
    type = "TXT"
    name = "mailo._domainkey"
    value = "k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDX16UZfYbYtEPC/4GgUkf7wGmLotT4Oh/I8QnmirMacjxqNQ+X+U7LY2VMC8wpeoTmv9a4H2GDqcCBoQsdDOTLu1NcN3DRBXrbDkndqQkwRW6vC8XhIXra2xyykKsOPUhuP4afNCcloV832tq4Y/BTGb5zqWeoBLi+BTDeYLh1lwIDAQAB"
}
