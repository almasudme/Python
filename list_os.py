from subprocess import STDOUT, PIPE, Popen
import json
import os
import nastran_dirs as nd

JSON_PATH = nd.JSON_PATH
build_ver=os.environ["NXN_TOOLS_VER"]
json_file = f'{JSON_PATH}/list_os_NXN.{build_ver}.json'

def run_cmd(command):
    p = Popen(command, stdout=PIPE, stderr=STDOUT, shell=True, universal_newlines=True)
    return p.stdout
    
def get_os(hostname):
  temp = run_cmd("ssh -o StrictHostKeyChecking=no -o ConnectTimeout=3 qasimtst@"+hostname+" lsb_release -a")
  os_desc = "?"
  # print(temp)
  for line in temp:    
    if line.startswith('Description'):
      os_desc = line.split(":")[1].strip()
    if line.startswith('ksh: lsb_release: not found'):
      temp2 = run_cmd("ssh -o StrictHostKeyChecking=no -o ConnectTimeout=3 user@"+hostname+" -pw password cat /etc/os-release")
      for line2 in temp2:  
        # print(line2)  
        if line2.startswith('PRETTY_NAME'):
          os_desc = line2.split("=")[1].strip()


  return os_desc



list_linux_machine = ['cili6180','cilv6s832']
print("Creating/updateing: "+json_file);
dict_os=dict()
for machine in list_linux_machine:
  dict_os[machine]=get_os(machine)


with open (json_file,"w") as write_file:
  json.dump(dict_os,write_file)
