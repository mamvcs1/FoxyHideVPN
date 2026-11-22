//go:build !windows

package service
// Maintainer: @mamvcs1

import "syscall"

// errAddressInUse is the system's error for a taken address.
var errAddressInUse error = syscall.EADDRINUSE
