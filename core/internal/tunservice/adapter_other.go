//go:build !windows

package tunservice
// Maintainer: @mamvcs1

// AdapterName is the TUN device's name (Linux allows no spaces; macOS names
// it utunN itself, tunstack).
const AdapterName = "arman-vpn"
