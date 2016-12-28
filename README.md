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


## usage

    ./zonefiler <zonedata-dir> <output-dir>


## example usage

    $ ./zonefiler.py example/ output/
    zonefiler v1.1 Dec 2016, written by Dan Luedtke <mail@danrl.com>
    loading default.yml
    loading zones.yml
    writing output/example.com
    writing output/2.0.192.in-addr.arpa
    writing output/0.0.0.0.8.b.d.0.1.0.0.2.ip6.arpa

The result:

    danrl@tunafish zonefiler2$ ls output/
    0.0.0.0.8.b.d.0.1.0.0.2.ip6.arpa	example.com
    2.0.192.in-addr.arpa


### 2.0.192.in-addr.arpa

    ;
    ; zone file for 2.0.192.in-addr.arpa
    ; generated 2016-12-28 19:02:54
    ;
    2.0.192.in-addr.arpa.                                                       1800   IN SOA    ns1.example.com. admin@example.com. ( 2016122801 14400 3600 1209600 3600 )
    2.0.192.in-addr.arpa.                                                       1800   IN NS     ns1.example.com.
    2.0.192.in-addr.arpa.                                                       1800   IN NS     ns2.example.net.
    2.0.192.in-addr.arpa.                                                       1800   IN NS     ns3.example.net.


### 0.0.0.0.8.b.d.0.1.0.0.2.ip6.arpa

    ;
    ; zone file for 0.0.0.0.8.b.d.0.1.0.0.2.ip6.arpa
    ; generated 2016-12-28 19:02:54
    ;
    0.0.0.0.8.b.d.0.1.0.0.2.ip6.arpa.                                           1800   IN SOA    ns1.example.com. admin@example.com. ( 2016122801 14400 3600 1209600 3600 )
    0.0.0.0.8.b.d.0.1.0.0.2.ip6.arpa.                                           1800   IN NS     ns1.example.com.
    0.0.0.0.8.b.d.0.1.0.0.2.ip6.arpa.                                           1800   IN NS     ns2.example.net.
    0.0.0.0.8.b.d.0.1.0.0.2.ip6.arpa.                                           1800   IN NS     ns3.example.net.


### example.com

    ;
    ; zone file for example.com
    ; generated 2016-12-28 19:02:54
    ;
    example.com.                                                                1800   IN SOA    ns1.example.com. admin@example.com. ( 2016122801 14400 3600 1209600 3600 )
    example.com.                                                                1800   IN NS     ns1.example.com.
    example.com.                                                                1800   IN NS     ns2.example.net.
    example.com.                                                                1800   IN NS     ns3.example.net.
