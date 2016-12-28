#!/usr/bin/env python3

import os
import sys
import yaml
import time
import ipaddress


# --- configuration ---------------------------------------------------------- #

conf_justify_name = 75
conf_justify_ttl = 6
conf_justify_rrtype = 6
conf_seconds_per_unit = {
  "s": 1,
  "m": 60,
  "h": 3600,
  "d": 86400,
  "w": 604800
}
conf_tlsa_usage = {
  "pkix-ta": 0,
  "pkix-ee": 1,
  "dane-ta": 2,
  "dane-ee": 3
}
conf_tlsa_selector = {
  "cert": 0,
  "spki": 1
}
conf_tlsa_matching_type = {
  "no-hash": 0,
  "sha-256": 1,
  "sha-512": 2
}
conf_required_default = (
  'auth_ns', 'ns', 'admin', 'refresh', 'retry', 'expire', 'minimum', 'ttl'
)


# --- convert time duration string to seconds -------------------------------- #

def to_sec(s):
  s = str(s)
  if s.isnumeric():
    return s
  else:
    return str(int(s[:-1]) * conf_seconds_per_unit[s[-1]])


# --- convert variable to list ----------------------------------------------- #

def to_list(v):
  if isinstance(v, list):
    return v
  return [ str(v) ]


# --- write zone file head --------------------------------------------------- #

def put_head(f, name, zone, serial):
  f.write(";\n" +                                                              \
          "; zone file for " + name + "\n" +                                    \
          "; generated " + time.strftime("%Y-%m-%d %H:%M:%S") + "\n" +         \
          ";\n")
  put_rr(f, name, zone['ttl'], "SOA",
         zone['auth_ns'] + ". " + zone['admin'] + ". " +                       \
         "( " +                                                                \
              str(serial) + " " +                                              \
              to_sec(zone['refresh']) + " " +                                  \
              to_sec(zone['retry']) + " " +                                    \
              to_sec(zone['expire'])  + " " +                                  \
              to_sec(zone['minimum']) + " " +                                  \
         ")")
  put_rr(f, name, zone['ttl'], "NS", zone['auth_ns'] + ".")
  for ns in zone['ns']:
    put_rr(f, name, zone['ttl'], "NS", ns + ".")


# --- write raw resource record ---------------------------------------------- #

def put_rr(f, name, ttl, rrtype, rrvalue):
  if not name.endswith('.'):
    name += '.'
  if isinstance(rrvalue, list):
    for v in rrvalue:
      f.write(name.ljust(conf_justify_name) + " " +                            \
              to_sec(ttl).ljust(conf_justify_ttl) + " " +                      \
              "IN " +                                                          \
              rrtype.ljust(conf_justify_rrtype) + " " +                        \
              str(v) + "\n")
  else:
    f.write(name.ljust(conf_justify_name) + " " +                              \
            to_sec(ttl).ljust(conf_justify_ttl) + " " +                        \
            "IN " +                                                            \
            rrtype.ljust(conf_justify_rrtype) + " " +                          \
            str(rrvalue) + "\n")


# --- write extra resource records ------------------------------------------- #

def put_extra_rr(f, host, ttl):
  name = host['host']
  if 'txt' in host.keys():
    put_rr(f, name, ttl, "TXT", host['txt'])
  if 'spf' in host.keys():
    put_rr(f, name, ttl, "SPF", host['spf'])
    put_rr(f, name, ttl, "TXT", host['spf'])
  if 'mx' in host.keys():
    for v in host['mx']:
      put_rr(f, name, ttl, "MX", str(v['prio']) + " " + v['name'] + ".")
  if 'cname' in host.keys():
    # multiples violates RFC, but bind can do round robin
    put_rr(f, name, ttl, "CNAME", host['cname'] + ".")
  if 'tlsa' in host.keys():
    for v in host['tlsa']:
      for port in to_list(v['ports']):
        put_rr(f, "_" + str(port) + "._" + v['protocol'] + "." + name, ttl,
               "TLSA",
               str(conf_tlsa_usage[v['usage']]) + " " +                        \
               str(conf_tlsa_selector[v['selector']]) + " " +                  \
               str(conf_tlsa_matching_type[v['matching_type']]) + " " +        \
               str(v['matching']))


# --- check if hostname is part of zone -------------------------------------- #

def host_in_zone(host, zone):
  return host[-(len(zone) + 1):] == "." + zone or host == zone


# --- main ------------------------------------------------------------------- #

def main():
  yml = []
  zones = []
  reverse_zones = []
  hosts = []

  print("zonefiler v1.1 Dec 2016, written by Dan Luedtke <mail@danrl.com>")

  if len(sys.argv) != 3:
    print("usage: ./zonefiler <input-dir> <output-dir>")
    sys.exit(1)

  # load database
  for file in os.listdir(str(sys.argv[1]) + "/realms/") + \
    ["../zones.yml", "../default.yml"]:
    if file.endswith(".yml"):
      print("loading", file)
      try:
        f = open(str(sys.argv[1]) + "/realms/" + file, 'r')
        yml += yaml.load(f.read())
        f.close()
      except:
        print("error loading", file)
        sys.exit(1)

  # find zone default parameters
  default = None
  for item in yml:
    if 'default' in item.keys():
      default = item
  if default == None:
    print("missing zone default parameters")
    sys.exit(1)

  # validate zone default parameters
  if not all (k in default for k in conf_required_default):
    print("missing one of", conf_required_default, "in default zone")
    sys.exit(1)

  # split zones, reverse_zones, and hosts
  for item in yml:
    if 'zone' in item.keys() or 'reverse_zone' in item.keys():
      for k in conf_required_default:
        if k not in item.keys():
          item[k] = default[k]
    if 'zone' in item.keys():
      zones.append(item)
    elif 'reverse_zone' in item.keys():
      reverse_zones.append(item)
    elif 'host' in item.keys():
      hosts.append(item)

  # free memory (well, i know it's python, but because i can...)
  yml = None

  # read/write serial
  serial = '0'
  try:
    f = open(str(sys.argv[1]) + '/serial', 'r')
    serial = f.readline()
    f.close()
  except:
    print('warning: could not read serial')
  if serial[:8] == time.strftime('%Y%m%d'):
    serial = str(int(serial) + 1)
  else:
    serial = time.strftime('%Y%m%d00')
  try:
    f = open(str(sys.argv[1]) + '/serial', 'w')
    f.write(serial)
    f.close
  except:
    print('warning: could not save serial')

  # export zones
  for zone in zones:
    fname = str(sys.argv[2]) + "/" + zone['zone']
    print("writing", fname)
    try:
      f = open(fname, 'w')
    except:
      print("error opening", fname, "for writing")
      sys.exit(1)
    put_head(f, zone['zone'], zone, serial)
    for host in hosts:
      if host_in_zone(host['host'], zone['zone']):
        if 'ip' in host.keys():
          for v in to_list(host['ip']):
            ip = ipaddress.ip_address(v)
            if ip.version == 4:
              put_rr(f, host['host'], zone['ttl'], "A", ip)
            elif ip.version == 6:
              put_rr(f, host['host'], zone['ttl'], "AAAA", ip)
        put_extra_rr(f, host, zone['ttl'])
    f.close()

  # export reverse zones
  for zone in reverse_zones:
    net = ipaddress.ip_network(zone['reverse_zone'])
    ip = ipaddress.ip_interface(zone['reverse_zone']).ip
    name = ip.reverse_pointer
    if ip.version == 4:
      for _ in range(int((32 - net.prefixlen) / 8)):
        name = name[name.index('.') + 1:]
    elif ip.version == 6:
      name = name[int((128 - net.prefixlen) / 2):]
    fname = str(sys.argv[2]) + "/" + name
    print("writing", fname)
    try:
      f = open(fname, 'w')
    except:
      print("error opening", fname, "for writing")
      sys.exit(1)
    put_head(f, name, zone, serial)
    for host in hosts:
      if 'ip' in host.keys():
        for v in to_list(host['ip']):
          ip = ipaddress.ip_address(v)
          if ip in net:
            put_rr(f, ip.reverse_pointer, zone['ttl'], "PTR",
                   host['host'] + ".")
      if host_in_zone(host['host'], name):
        put_extra_rr(f, host, zone['ttl'])
    f.close()


if __name__ == "__main__":
  main()
