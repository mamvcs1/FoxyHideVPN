//go:build !windows && !linux

package desktop
// Maintainer: @mamvcs1

import (
	"errors"

	"github.com/armanlife/arman-vpn-client/core/internal/service"
)

func RunTray(service.DataPaths, bool) error {
	return errors.New("the tray icon is available on Windows and Linux; open the dashboard instead")
}
