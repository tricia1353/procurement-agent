"""
企业查询服务封装
"""

from typing import Dict, Any, List


class EnterpriseService:
    """企业查询服务"""

    async def search_company(self, keyword: str) -> List[Dict[str, Any]]:
        """
        搜索企业

        Args:
            keyword: 企业名称关键词

        Returns:
            匹配的企业列表
        """
        return self._mock_search(keyword)

    async def get_company_detail(self, company_id: int) -> Dict[str, Any]:
        """
        获取企业详情

        Args:
            company_id: 企业ID

        Returns:
            企业详细信息
        """
        return self._mock_detail(company_id)

    def _mock_search(self, keyword: str) -> List[Dict[str, Any]]:
        """模拟搜索数据 - 覆盖常见电子元器件供应商"""
        mock_companies = [
            # 深圳地区
            {"id": 1, "name": "深圳华强电子有限公司", "regStatus": "存续", "regCapital": "5000万元人民币", "legalPersonName": "张伟", "province": "广东", "city": "深圳"},
            {"id": 2, "name": "深圳立创商城电子商务有限公司", "regStatus": "存续", "regCapital": "8000万元人民币", "legalPersonName": "王强", "province": "广东", "city": "深圳"},
            {"id": 3, "name": "深圳云汉电子有限公司", "regStatus": "存续", "regCapital": "3000万元人民币", "legalPersonName": "刘波", "province": "广东", "city": "深圳"},
            {"id": 4, "name": "深圳捷扬电子科技有限公司", "regStatus": "存续", "regCapital": "1000万元人民币", "legalPersonName": "陈明", "province": "广东", "city": "深圳"},
            {"id": 5, "name": "深圳芯邦科技有限责任公司", "regStatus": "存续", "regCapital": "2000万元人民币", "legalPersonName": "赵军", "province": "广东", "city": "深圳"},
            # 东莞地区
            {"id": 6, "name": "东莞立创电子商务有限公司", "regStatus": "存续", "regCapital": "2000万元人民币", "legalPersonName": "王强", "province": "广东", "city": "东莞"},
            {"id": 7, "name": "东莞伟文电子有限公司", "regStatus": "存续", "regCapital": "500万元人民币", "legalPersonName": "李伟", "province": "广东", "city": "东莞"},
            # 上海地区
            {"id": 8, "name": "上海贸泽电子贸易有限公司", "regStatus": "存续", "regCapital": "3000万元人民币", "legalPersonName": "李明", "province": "上海", "city": "上海"},
            {"id": 9, "name": "上海得捷电子中国代表处", "regStatus": "存续", "regCapital": "500万美元", "legalPersonName": "John Smith", "province": "上海", "city": "上海"},
            {"id": 10, "name": "上海润欣科技股份有限公司", "regStatus": "存续", "regCapital": "1亿元人民币", "legalPersonName": "黄俊", "province": "上海", "city": "上海"},
            # 北京地区
            {"id": 11, "name": "北京创毅视讯科技有限公司", "regStatus": "存续", "regCapital": "2000万元人民币", "legalPersonName": "张磊", "province": "北京", "city": "北京"},
            {"id": 12, "name": "北京君正集成电路股份有限公司", "regStatus": "存续", "regCapital": "2亿元人民币", "legalPersonName": "刘强", "province": "北京", "city": "北京"},
            # 杭州地区
            {"id": 13, "name": "杭州中芯微电子有限公司", "regStatus": "存续", "regCapital": "1500万元人民币", "legalPersonName": "周华", "province": "浙江", "city": "杭州"},
            {"id": 14, "name": "杭州士兰微电子股份有限公司", "regStatus": "存续", "regCapital": "5亿元人民币", "legalPersonName": "陈向东", "province": "浙江", "city": "杭州"},
            # 苏州地区
            {"id": 15, "name": "苏州固锝电子股份有限公司", "regStatus": "存续", "regCapital": "3亿元人民币", "legalPersonName": "吴念博", "province": "江苏", "city": "苏州"},
            {"id": 16, "name": "苏州晶方半导体科技股份有限公司", "regStatus": "存续", "regCapital": "2亿元人民币", "legalPersonName": "王蔚", "province": "江苏", "city": "苏州"},
            # 南京地区
            {"id": 17, "name": "南京沁恒微电子股份有限公司", "regStatus": "存续", "regCapital": "1000万元人民币", "legalPersonName": "张震", "province": "江苏", "city": "南京"},
            # 成都地区
            {"id": 18, "name": "成都华微电子科技股份有限公司", "regStatus": "存续", "regCapital": "5000万元人民币", "legalPersonName": "李勇", "province": "四川", "city": "成都"},
            # 西安地区
            {"id": 19, "name": "西安紫光国芯半导体有限公司", "regStatus": "存续", "regCapital": "1亿元人民币", "legalPersonName": "任军", "province": "陕西", "city": "西安"},
            # 厦门地区
            {"id": 20, "name": "厦门士兰集科微电子有限公司", "regStatus": "存续", "regCapital": "8000万元人民币", "legalPersonName": "陈向东", "province": "福建", "city": "厦门"},
            # 国际代理商
            {"id": 21, "name": "艾睿电子中国有限公司", "regStatus": "存续", "regCapital": "1000万美元", "legalPersonName": "Mike Johnson", "province": "上海", "city": "上海"},
            {"id": 22, "name": "安富利中国有限公司", "regStatus": "存续", "regCapital": "800万美元", "legalPersonName": "David Brown", "province": "上海", "city": "上海"},
        ]

        # 模糊匹配
        keyword_lower = keyword.lower()
        matches = [c for c in mock_companies if keyword_lower in c["name"].lower()]

        # 如果没有精确匹配，尝试关键词匹配
        if not matches:
            keywords = keyword_lower.replace("电子", "").replace("科技", "").replace("有限", "")
            matches = [c for c in mock_companies if any(k in c["name"].lower() for k in keywords.split() if len(k) > 1)]

        return matches[:10]  # 最多返回10条

    def _mock_detail(self, company_id: int) -> Dict[str, Any]:
        """模拟详情数据"""
        mock_details = {
            1: {
                "id": 1,
                "name": "深圳华强电子有限公司",
                "creditCode": "91440300MA5EXXXXXXX",
                "legalPersonName": "张伟",
                "regCapital": "5000万元人民币",
                "regStatus": "存续",
                "estiblishTime": "2010-05-18",
                "businessScope": "电子元器件、集成电路、电子产品的销售",
                "province": "广东",
                "city": "深圳",
                "address": "深圳市福田区华强北街道XX路XX号"
            }
        }

        return mock_details.get(company_id, {})