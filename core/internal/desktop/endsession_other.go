//go:build !windows

package desktop
// Maintainer: @mamvcs1

// watchEndSession: elsewhere the session's end reaches the core as SIGTERM,
// which the app mode already handles.
func watchEndSession(func()) (func(), error) { return func() {}, nil }
