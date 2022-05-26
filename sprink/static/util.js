const util = (() => {
	cron = /(@(annually|yearly|monthly|weekly|daily|hourly|reboot))|(@every (\d+(ns|us|µs|ms|s|m|h))+)|((((\d+,)+\d+|(\d+(\/|-)\d+)|\d+|\*) ?){5,7})/;

	return {
		isCronValid: (r) => {
			return cron.test(r)
		}
	}
})()