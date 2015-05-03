from descriptor.httpresponse import HttpResponse
from descriptor.hostbyname import HostByName
from cloudflarenetwork import CloudFlareNetwork


class Target:

    def __init__(self, name, domain, port=None, timeout=10, ssl=False):
        self.domain = domain
        self.name = name
        self.ip = HostByName(domain).__get__()
        if self.ip:
            self.response = HttpResponse(domain, port, timeout, ssl).__get__()

    @property
    def cloudflare_ip(self):
        net = CloudFlareNetwork()
        return net.in_range(self.ip)

    @property
    def cloudflare_ray(self):
        try:
            return self.response.getheader('CF-RAY')
        except:
            return None

    @property
    def enabled(self):
        try:
            if self.response.getheader('X-Powered-By'):
                return self.response.getheader('Server') \
                    + ' ' \
                    + self.response.getheader('X-Powered-By')
            else:
                return self.response.getheader('Server')
        except:
            return None

    @property
    def status(self):
        try:
            return self.response.status
        except:
            return None

    @property
    def reason(self):
        try:
            return self.response.reason
        except:
            return None

    @property
    def protected(self):
        return bool(self.cloudflare_ray)

    def print_infos(self):
        print('['+self.name+'] '+self.domain)
        if not self.ip:
            print('> not-found')
            return

        print(
            '> ip: %s (CF %s%s)' % (
                self.ip,
                'yes' if self.cloudflare_ip else 'no',
                ' RAY-'+self.cloudflare_ray if self.cloudflare_ray else ''
            )
        )

        if self.enabled:
            print(
                '> http: %s %s %s' % (
                    self.enabled+' -' if self.enabled else '',
                    self.status,
                    self.reason if self.reason else ''
                )
            )
