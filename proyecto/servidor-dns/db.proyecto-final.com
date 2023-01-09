$TTL    604800
@       IN      SOA     ns1.proyecto-final.com. root.proyecto-final.com. (
                  3       ; Serial
             604800       ; Refresh
              86400       ; Retry
            2419200       ; Expire
             604800 )     ; Negative Cache TTL
;

; name servers - NS records
     IN      NS      ns1.proyecto-final.com.

; name servers - A records
ns1.proyecto-final.com.        IN      A      192.168.10.10
web.proyecto-final.com.        IN      A      192.168.11.10
api.proyecto-final.com.        IN      A      192.168.0.10
externo.proyecto-final.com     IN      A      20.20.20.20