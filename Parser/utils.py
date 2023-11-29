def padding_number(number_list):
  print(111111111111, number_list)
  ret = []
  ret.append(number_list[0])
  ret.append(number_list[1])
  unit_price = number_list[-2]
  total_price = number_list[-1]
  units = float(total_price.replace('$', '').replace(',', '')) / float(unit_price.replace('$', '').replace(',', ''))
  ret.append(round(units))
  ret.append(number_list[-3].split(' ')[1] if ' ' in number_list[-3] else number_list[-3])
  ret.append(number_list[-2])
  ret.append(number_list[-1])
  return ret

def get_text_cluster_by_starter(text_cluster, starter):
  idx = 0
  for key, value in text_cluster.get('cluster').items():
    if starter in value[0]:
      idx = key
      break
  return text_cluster.get('cluster').get(idx)