# Utils

# Traceout a container



## Check standard output

```
curl -v -X GET http://cognet:here4cognet@[docker_ip]:4242/containers/your_docker_container_name/logs?stdout=1&follow=1
```

## Check error output

```
curl -v -X GET http://cognet:here4cognet@[docker_ip]:4242/containers/your_docker_container_name/logs?stderr=1&follow=1
```

_**In order to get the specific IP address of any Common Infrastructure machine check the hosts file**_ [https://github.com/CogNet-5GPPP/demos_public/blob/master/hosts](https://github.com/CogNet-5GPPP/demos_public/blob/master/hosts)

your_docker_container_name must be the same than the one you set up in your ansible.yml file:

```
- name: Create a data container
  hosts: docker
  remote_user: "{{ansible_user}}"
  become: yes
  vars:
    hosts_ip: "{ \"spark_master\":\"{{ hostvars.spark_master.ansible_ssh_host }}\",\"spark_slaves1\":\"{{ hostvars.spark_slaves1.ansible_ssh_host }}\", \"spark_slaves2\":\"{{ hostvars.spark_slaves2.ansible_ssh_host }}\", \"oscon\":\"{{ hostvars.oscon.ansible_ssh_host }}\",\"odl\":\"{{ hostvars.odl.ansible_ssh_host }}\",\"monasca\":\"{{ hostvars.monasca.ansible_ssh_host }}\",\"docker\":\"{{ hostvars.docker.ansible_ssh_host }}\",\"kafka\":\"{{ hostvars.kafka.ansible_ssh_host }}\",\"policy\":\"{{ hostvars.policy.ansible_ssh_host }}\"}"
  tasks:
    - name: Remove container
      docker_container:
        name: your_docker_container_name
        image: "mydemo:ontheedge"
        state: absent
    - name: Create Container
      docker_container:
        name: your_docker_container_name
        image: "mydemo:ontheedge"
        state: started
        etc_hosts: "{{ hosts_ip }}"
```




