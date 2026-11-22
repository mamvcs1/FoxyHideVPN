//go:build !windows && !linux

package netstate
// Maintainer: @mamvcs1

func connected() bool { return true }

func current() (string, bool) { return "", false }
