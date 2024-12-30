# macOS Local Certificate Authority for Development

This repository contains a minimal demonstration of how to set up a
system-trusted certificate authority on macOS using cfssl. This is useful for
running local development servers with full TLS support, getting rid of
annoying warning screens about insecure protocols, and the occasional hacks
required to set up services for insecure connections.

This is meant to be the absolute bare minimal functional demonstration. You may
wish to add details to your certificates by editing the JSON files. Additional
automation and scripting can be used to make a more ergonomic developer
experience, but this shows that what's going on is conceptually rather simple.
You won't really use any of the code in this repository directly, rather it's to
show what's required to set things up up on macOS, and then you incorporate that
process into your own, or your team's or organization's, development process.

The main thing that's happening is a key and certificate are being generated,
and the certificate is added to the macOS System keychain, and "trusted". That
is all that's required to establish the system. The remainder of the operations
performed are just for demonstration -- creating an intermediate certificate
authority and server certificate, starting a python https server, and using curl
to confirm it's working -- these are not actual steps you must perform.

If everyone on a team performs this minimal setup, and stores the key and
certificate in the same place, for example `~/.local/share/ca`, then it becomes
much easier to automate TLS usage for local development across all repositories
for an organization.

This can be used with a DNS service like [sslip.io](https://sslip.io) to have
unlimited local subdomains of `127.0.0.1.sslip.io`, or any other IP address,
which can then be protected with TLS certificates generated by cfssl, including
wildcard certificates. Alternatively, a local DNS server offers even more
control over DNS.

This setup could be performed once per project instead of system-wide, but that
entails more actions requiring superuser permissions (adding keys to the macOS
System keychain), so a system-wide impelementation seems less disruptive.

## Dependencies

You must install [cfssl](https://github.com/cloudflare/cfssl) to run the setup.
It can be installed using [Homebrew](https://brew.sh/) with the command
`brew install cfssl`. Python and curl are also required, but are shipped with
macOS, so should not require installation.

## Quickstart

Run `./setup` from the root of the repository. This will do the following:

1. Create a root certificate authority key and self-signed certificate.
2. Add the root certificate to the macOS System keychain (requires superuser
   privileges.)
3. Create an intermediate certificate authority key and certificate signed by
   the root certificate authority.
4. Create a server key and certificate signed by the intermediate certificate
   authority.
5. Launch a Python server and use `curl` to run an end-to-end request and
   ensures the root certificate is correctly trusted.

This requries internet connectivity, since `127.0.0.1.sslip.io` is used, and
must be resolvable over DNS. Alternatively, you can override that hostname in
`/etc/hosts`, and then internet connectivity is not required.

## Security

A trusted root certificate is a powerful thing. Typically the private keys for
these are kept offline, and only accessed when creating new intermediate
certificate authorities and/or revoking them.

Since this is just for local development, and will only be trusted by one
computer, the potential blast radius for shenanigans with this key are less,
but still nonzero. Leaving this key in the filesystem with reasonable
permissions is probably not the worst thing in the world.

You may wish to move the root key offline, or encrypt it locally, or do any
number of other things to secure it. At the end of the day, this is a trusted
root certificate, and that comes with some risks and responsibilities. Use
wisely.

## Teardown

Overall, the scripts in this repository don't interact with anything outside of
the local directory. The one exception is that the root certificate is
registered in the macOS System keychain. To remove a certificate you're no
longer using, you can open `Keychain Access`, go to `System` in the
`System Keychains` section of the left sidebar, and you should see the
`Local Development Root Certificate Authority` (or another name, if you
customized it). You can right-click the entry and click `Delete` to delete the
certificate.

In theory you should only need to set up the root certificate once, and then
continue using it until its expiration, so you should not need to manually
remove root certificates from the key store often, unless you're working on
these scripts themselves.

# The Real Minimum

The `setup` script is a a full end-to-end demonstration, but if you're
developing locally on Kubernetes with something like minikube or k3s, and using
cert-manager to generate certificates, then all you really need to do is
generate a self-signed root certificate, which can be given to cert-manager to
start a CA Issuer, and add it to the macOS System keychain. So, the real minimum
setup looks more like this:

```sh
brew install cfssl
echo '{ "CN": "Root CA", "key": { "algo": "ecdsa", "curve": "P-256"} }' | \
  cfssl genkey -initca - | cfssljson -bare root
sudo security add-trusted-cert -d -r trustRoot \
  -k /Library/Keychains/System.keychain root.pem
```

After running these commands, you should have `root.pem`, `root-key.pem`, and
`root.csr`. The `root.csr` file can be discarded if desired, and the other two
files can be added to Kubernetes in a `Secret` (in `tls.crt` and `tls.key`, and
then used by `cert-manager` to create a `ClusterIssuer`.
