# zonefiler

A tool for creating forward and reverse zone files for hosts described in YAML.


## Realms

* A realm is a logical collection of forward zone data.
* A realm may contain forward zone data from different domains.
* A domain's forward zone data may be spread over multiple realms.
* Each realm has it's own realm file named `realms/<realm>.yml`.
* The behavior in case of duplicate entries is undefined.


## Zones

* Default settings for zone files are stored in `default.yml`
* Zone files are only generated for zones in `zones.yml`.
* Reverse zones and PTR RR are auto-generated.


## Usage

    $ ./zonefiler <zonedata-dir> <output-dir>


## Example usage

    $ ./zonefiler.py example/ output/
    zonefiler v1.1 Dec 2016, written by Dan Luedtke <mail@danrl.com>
    loading myservers.yml
    loading ../zones.yml
    loading ../default.yml
    writing output/example.com
    writing output/2.0.192.in-addr.arpa
    writing output/0.0.0.0.8.b.d.0.1.0.0.2.ip6.arpa

The result:

    $ ls output/
    0.0.0.0.8.b.d.0.1.0.0.2.ip6.arpa
    2.0.192.in-addr.arpa
    example.com


### Input myrealm.yml

    - host: example.com
      ip:
        - 192.0.2.1
        - 2001:db8::1
      mx:
        - name: mail1.example.com
          prio: 10
        - name: mail2.example.com
          prio: 20

    - host: www.example.com
      cname: example.com

    - host: mail1.example.com
      ip:
        - 192.0.2.55
        - 2001:db8::55
      tlsa:
        - protocol: tcp
          ports: [ 25, 143, 587 ]
          usage: dane-ee
          selector: spki
          matching_type: sha-256
          matching: aaaaaaabbbbbbbccccccdddddddeeeeee42

    - host: cool.example.com
      ip:
        - 2001:db8::10:1
        - 2001:db8::10:2
        - 2001:db8::10:3

### Input zones.yml

    - zone: example.com
    - reverse_zone: 192.0.2.0/24
    - reverse_zone: 2001:db8::/48

### Output example.com

    ;
    ; zone file for example.com
    ; generated 2016-12-28 20:56:38
    ;
    example.com.                                                                1800   IN SOA    ns1.example.com. admin.example.com. ( 2016122806 14400 3600 1209600 3600 )
    example.com.                                                                1800   IN NS     ns1.example.com.
    example.com.                                                                1800   IN NS     ns2.example.net.
    example.com.                                                                1800   IN NS     ns3.example.net.
    example.com.                                                                1800   IN A      192.0.2.1
    example.com.                                                                1800   IN AAAA   2001:db8::1
    example.com.                                                                1800   IN MX     10 mail1.example.com.
    example.com.                                                                1800   IN MX     20 mail2.example.com.
    www.example.com.                                                            1800   IN CNAME  example.com.
    mail1.example.com.                                                          1800   IN A      192.0.2.55
    mail1.example.com.                                                          1800   IN AAAA   2001:db8::55
    _25._tcp.mail1.example.com.                                                 1800   IN TLSA   3 1 1 aaaaaaabbbbbbbccccccdddddddeeeeee42
    _143._tcp.mail1.example.com.                                                1800   IN TLSA   3 1 1 aaaaaaabbbbbbbccccccdddddddeeeeee42
    _587._tcp.mail1.example.com.                                                1800   IN TLSA   3 1 1 aaaaaaabbbbbbbccccccdddddddeeeeee42
    cool.example.com.                                                           1800   IN AAAA   2001:db8::10:1
    cool.example.com.                                                           1800   IN AAAA   2001:db8::10:2
    cool.example.com.                                                           1800   IN AAAA   2001:db8::10:3


### Output 0.0.0.0.8.b.d.0.1.0.0.2.ip6.arpa

    ;
    ; zone file for 0.0.0.0.8.b.d.0.1.0.0.2.ip6.arpa
    ; generated 2016-12-28 20:56:38
    ;
    0.0.0.0.8.b.d.0.1.0.0.2.ip6.arpa.                                           1800   IN SOA    ns1.example.com. admin.example.com. ( 2016122806 14400 3600 1209600 3600 )
    0.0.0.0.8.b.d.0.1.0.0.2.ip6.arpa.                                           1800   IN NS     ns1.example.com.
    0.0.0.0.8.b.d.0.1.0.0.2.ip6.arpa.                                           1800   IN NS     ns2.example.net.
    0.0.0.0.8.b.d.0.1.0.0.2.ip6.arpa.                                           1800   IN NS     ns3.example.net.
    1.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.8.b.d.0.1.0.0.2.ip6.arpa.   1800   IN PTR    example.com.
    5.5.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.8.b.d.0.1.0.0.2.ip6.arpa.   1800   IN PTR    mail1.example.com.
    1.0.0.0.0.1.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.8.b.d.0.1.0.0.2.ip6.arpa.   1800   IN PTR    cool.example.com.
    2.0.0.0.0.1.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.8.b.d.0.1.0.0.2.ip6.arpa.   1800   IN PTR    cool.example.com.
    3.0.0.0.0.1.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.8.b.d.0.1.0.0.2.ip6.arpa.   1800   IN PTR    cool.example.com.


### Output 2.0.192.in-addr.arpa

    ;
    ; zone file for 2.0.192.in-addr.arpa
    ; generated 2016-12-28 20:56:38
    ;
    2.0.192.in-addr.arpa.                                                       1800   IN SOA    ns1.example.com. admin.example.com. ( 2016122806 14400 3600 1209600 3600 )
    2.0.192.in-addr.arpa.                                                       1800   IN NS     ns1.example.com.
    2.0.192.in-addr.arpa.                                                       1800   IN NS     ns2.example.net.
    2.0.192.in-addr.arpa.                                                       1800   IN NS     ns3.example.net.
    1.2.0.192.in-addr.arpa.                                                     1800   IN PTR    example.com.
    55.2.0.192.in-addr.arpa.                                                    1800   IN PTR    mail1.example.com.
