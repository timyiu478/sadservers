## "Campina Grande": Give me my cert, Vault

### Problem

A web application running at https://nginx.example.com has an expired certificate. Issue a new certificate using the Hashicorp Vault running on the server.

The Vault instance is already unsealed and initialized, and you have full admin access with the admin user.

The certificate presented by Nginx is issued by the Vault PKI (check using openssl verify -CAfile /usr/local/share/ca-certificates/vault-pki-ca.crt /etc/nginx/ssl/cert.pem).

src: https://sadservers.com/scenario/campina-grande

### Solution

todo
