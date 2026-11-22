//go:build !linux

package tunstack
// Maintainer: @mamvcs1

// missingDriver: only Linux has a driver that may not be loaded.
func missingDriver(error) bool { return false }

func loadDriver() {}
