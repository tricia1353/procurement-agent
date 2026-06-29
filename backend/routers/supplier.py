"""
供应商寻源路由
- 支持按产品型号联网搜索供应商
- 自动查询企业工商信息
- 智能寻源（物料需求 + 替代供应商搜索）
- 面谈问题生成
"""

from fastapi import APIRouter, Header, HTTPException, Query
from typing import Optional, List
import asyncio

from models import (
    SupplierSearchRequest, SupplierSearchResponse, SupplierInfo,
    MaterialRequirement, SourcingRequest, SupplierMatch, SourcingResponse,
    InterviewQuestion, InterviewQuestionsRequest, InterviewQuestionsResponse
)
from services.llm import LLMService
from services.enterprise import EnterpriseService

router = APIRouter()

# 服务实例
llm_service = LLMService()
enterprise_service = EnterpriseService()


# 模拟供应商数据
MOCK_SUPPLIERS = [
    SupplierInfo(
        name="深圳华强电子",
        category="芯片/IC",
        region="广东深圳",
        source="行业推荐",
        cooperation_years=5,
        advantages=["原装正品", "交期稳定", "技术支持好"],
        issues=["价格偏高"],
        rating=4.2,
        credit_score=92,
        certifications=["ISO9001", "IATF16949"]
    ),
    SupplierInfo(
        name="上海贸泽电子",
        category="电子元器件",
        region="上海",
        source="网络搜索",
        cooperation_years=2,
        advantages=["品类齐全", "海外直采", "正品保障"],
        issues=["最小起订量大", "交期较长"],
        rating=3.8,
        credit_score=88,
        certifications=["ISO9001"]
    ),
    SupplierInfo(
        name="东莞立创商城",
        category="电子元器件",
        region="广东东莞",
        source="自主开发",
        cooperation_years=3,
        advantages=["价格实惠", "现货库存", "BOM配单"],
        issues=["部分型号缺货"],
        rating=4.5,
        credit_score=95,
        certifications=["ISO9001", "ISO14001"]
    ),
    SupplierInfo(
        name="杭州中芯微电子",
        category="芯片/IC",
        region="浙江杭州",
        source="展会认识",
        cooperation_years=1,
        advantages=["MCU专业", "技术支持强", "可定制"],
        issues=["品类较窄"],
        rating=4.0,
        credit_score=89,
        certifications=["ISO9001", "IATF16949", "ISO14001"]
    ),
    SupplierInfo(
        name="深圳晶显科技",
        category="液晶/显示屏",
        region="广东深圳",
        source="客户推荐",
        cooperation_years=2,
        advantages=["价格优势", "定制能力强"],
        issues=["品质波动", "交期不稳定"],
        rating=3.5,
        credit_score=78,
        certifications=["ISO9001"]
    )
]


@router.post("/search", response_model=SupplierSearchResponse)
async def search_suppliers(
    request: SupplierSearchRequest,
    x_llm_token: Optional[str] = Header(None, alias="X-LLM-Token")
):
    """
    搜索供应商

    优先级：
    1. 如果提供了产品型号(model) → LLM联网搜索供应商
    2. 否则使用本地MOCK数据按品类筛选

    自动补充企业工商信息
    """
    suppliers = []

    # 1. 如果提供了型号，使用LLM联网搜索
    if request.model and request.model.strip():
        model = request.model.strip().upper()
        print(f"🔍 使用LLM联网搜索供应商，型号: {model}")

        try:
            # 调用LLM联网搜索
            llm_result = await llm_service.search_suppliers_by_model(model)
            raw_suppliers = llm_result.get("suppliers", [])

            print(f"📋 LLM返回 {len(raw_suppliers)} 个供应商")

            # 转换并补充企业信息
            for s in raw_suppliers:
                supplier_name = s.get("name", "")
                if not supplier_name:
                    continue

                # 查询企业工商信息
                enterprise_info = await _get_enterprise_info(supplier_name)

                supplier_info = SupplierInfo(
                    name=supplier_name,
                    category=s.get("category", request.category or "电子元器件"),
                    region=s.get("region", ""),
                    source=s.get("source", "网络搜索"),
                    advantages=s.get("advantages", []),
                    issues=[],
                    credit_score=enterprise_info.get("credit_score", 75),
                    certifications=enterprise_info.get("certifications", []),
                    contact=enterprise_info.get("contact")
                )
                suppliers.append(supplier_info)

            # 按地区筛选
            if request.region:
                suppliers = [s for s in suppliers if request.region in (s.region or "")]

        except Exception as e:
            print(f"❌ LLM搜索失败: {e}")
            # 降级到MOCK数据
            suppliers = _search_mock_suppliers(request.category, request.region)

    else:
        # 2. 没有型号，使用MOCK数据
        print(f"📁 使用本地MOCK数据筛选，品类: {request.category}")
        suppliers = _search_mock_suppliers(request.category, request.region)

    # 生成摘要
    summary = {
        "total_found": len(suppliers),
        "recommendation": _generate_recommendation(suppliers),
        "notes": "建议优先联系信用评分高、资质齐全的供应商"
    }

    return SupplierSearchResponse(
        category=request.category or "全部",
        suppliers=suppliers,
        summary=summary
    )


async def _get_enterprise_info(company_name: str) -> dict:
    """查询企业工商信息"""
    try:
        companies = await enterprise_service.search_company(company_name)
        if companies:
            # 取第一个匹配结果
            company = companies[0]
            return {
                "credit_score": 80 + (hash(company_name) % 15),  # 模拟评分
                "certifications": ["ISO9001"],  # 模拟资质
                "contact": {
                    "address": company.get("province", "") + company.get("city", ""),
                    "legal_person": company.get("legalPersonName", "")
                }
            }
    except Exception as e:
        print(f"⚠️ 查询企业信息失败: {e}")

    return {}


def _search_mock_suppliers(category: Optional[str], region: Optional[str]) -> List[SupplierInfo]:
    """从MOCK数据中筛选供应商"""
    matched = []
    for supplier in MOCK_SUPPLIERS:
        if category and category not in (supplier.category or ""):
            continue
        if region and region not in (supplier.region or ""):
            continue
        matched.append(supplier)
    return matched


@router.get("/detail")
async def get_supplier_detail(
    name: str = Query(..., description="供应商名称")
):
    """
    获取供应商详情

    - 企业基本信息
    - 资质证书
    - 信用评分
    """
    # 查找供应商
    for supplier in MOCK_SUPPLIERS:
        if name in supplier.name or supplier.name in name:
            return {
                "found": True,
                "supplier": supplier.model_dump(),
                "enterprise_info": {
                    "credit_code": "91440300MA5EXXXXXXX",
                    "legal_person": "张伟",
                    "registered_capital": "5000万元人民币",
                    "established_date": "2010-05-18",
                    "business_status": "存续",
                    "business_scope": "电子元器件、集成电路、电子产品的销售..."
                }
            }

    return {
        "found": False,
        "message": f"未找到供应商: {name}"
    }


@router.get("/check-qualification")
async def check_qualification(
    name: str = Query(..., description="供应商名称"),
    certifications: str = Query(..., description="要求的资质证书，逗号分隔")
):
    """
    检查供应商资质

    - 验证是否具备要求的资质证书
    - 返回资质匹配结果
    """
    required_certs = [c.strip() for c in certifications.split(",")]

    # 查找供应商
    for supplier in MOCK_SUPPLIERS:
        if name in supplier.name or supplier.name in name:
            supplier_certs = supplier.certifications or []

            matched = []
            missing = []
            for cert in required_certs:
                if any(cert.lower() in c.lower() for c in supplier_certs):
                    matched.append(cert)
                else:
                    missing.append(cert)

            return {
                "found": True,
                "supplier_name": supplier.name,
                "credit_score": supplier.credit_score,
                "risk_level": "低风险" if supplier.credit_score >= 80 else "中风险",
                "certifications": supplier_certs,
                "required_certs": required_certs,
                "matched_certs": matched,
                "missing_certs": missing,
                "qualified": len(missing) == 0,
                "recommendation": _generate_qualification_advice(supplier, missing)
            }

    return {
        "found": False,
        "message": f"未找到供应商: {name}"
    }


def _generate_recommendation(suppliers: List[SupplierInfo]) -> str:
    """生成推荐建议"""
    if not suppliers:
        return "未找到匹配的供应商"

    # 按信用评分排序
    sorted_suppliers = sorted(suppliers, key=lambda x: x.credit_score or 0, reverse=True)
    top = sorted_suppliers[0]

    return f"推荐优先联系「{top.name}」，信用评分 {top.credit_score}，资质齐全"


def _generate_qualification_advice(supplier: SupplierInfo, missing: List[str]) -> str:
    """生成资质建议"""
    if not missing:
        return "✅ 资质符合要求，建议优先合作"

    advice = []
    if supplier.credit_score and supplier.credit_score >= 85:
        advice.append("✅ 企业信用良好，风险较低")
    elif supplier.credit_score and supplier.credit_score < 80:
        advice.append("⚠️ 企业信用分较低，建议加强背景调查")

    if missing:
        advice.append(f"⚠️ 缺少资质: {', '.join(missing)}")

    return "；".join(advice)



@router.post("/sourcing", response_model=SourcingResponse)
async def sourcing(
    request: SourcingRequest,
    x_llm_token: Optional[str] = Header(None, alias="X-LLM-Token")
):
    """
    智能供应商寻源

    输入物料需求或当前供应商，系统自动：
    1. 联网搜索供应商
    2. 查询企业工商信息
    3. 返回推荐列表
    """
    suppliers = []
    search_sources = []
    search_details = None

    # 使用请求头中的 Token（优先）或默认配置
    current_llm = LLMService(token=x_llm_token) if x_llm_token else llm_service

    # ==================== 搜索来源：LLM 联网搜索 ====================
    if current_llm.is_configured():
        try:
            print(f"🌐 使用 LLM 联网搜索供应商")
            search_sources.append("联网搜索")

            # 准备搜索参数
            material_dict = request.material.model_dump()
            if request.preferred_regions:
                material_dict["preferred_regions"] = request.preferred_regions

            llm_result = await current_llm.sourcing_search(
                material_dict,
                request.current_supplier or ""
            )

            raw_suppliers = llm_result.get("suppliers", [])
            print(f"📋 LLM返回 {len(raw_suppliers)} 个供应商")

            # 检查是否有解析错误
            if llm_result.get("error"):
                print(f"⚠️ LLM返回解析错误: {llm_result.get('error')}")
                search_details = f"AI 解析结果时遇到问题，已为您推荐相关供应商"

            for s in raw_suppliers:
                supplier_name = s.get("name", "")
                if not supplier_name or any(sup.name == supplier_name for sup in suppliers):
                    continue

                match = SupplierMatch(
                    name=supplier_name,
                    region=s.get("region", ""),
                    category=s.get("category", ""),
                    products=s.get("products", []),
                    advantages=s.get("advantages", []),
                    served_clients=s.get("served_clients", []),
                    match_score=0,
                    certifications=[],
                    source=s.get("source", "联网搜索"),
                    risk_level="待确认",
                    credit_score=None
                )
                suppliers.append(match)
        except HTTPException:
            raise
        except Exception as e:
            print(f"❌ LLM 搜索失败: {e}")
            # LLM 搜索失败，使用 MOCK 数据作为降级方案
            print("⚠️ LLM 搜索失败，使用推荐供应商作为参考")
            search_details = f"AI 搜索遇到问题，已为您推荐相关供应商"

    # ==================== 如果 LLM 搜索无结果或未配置，使用 MOCK 数据作为推荐 ====================
    if not suppliers:
        if not current_llm.is_configured():
            print("⚠️ LLM 未配置，使用推荐供应商作为参考")
            search_details = f"LLM 服务未配置，以下为推荐供应商供参考。请配置 LLM Token 后使用实时搜索功能。"
            search_sources.append("推荐供应商")
        elif not search_details:
            print("⚠️ LLM 搜索无结果，使用推荐供应商作为参考")
            search_details = f"未找到「{request.material.model or request.material.category}」的直接供应商，以下为推荐供应商供参考"
            search_sources.append("推荐供应商")

        # 根据品类筛选 MOCK 数据
        category = request.material.category or ""
        for mock_sup in MOCK_SUPPLIERS:
            if category and category not in (mock_sup.category or ""):
                continue
            match = SupplierMatch(
                name=mock_sup.name,
                region=mock_sup.region or "",
                category=mock_sup.category or "",
                products=[mock_sup.category or "电子元器件"],
                advantages=mock_sup.advantages or [],
                served_clients=[],
                match_score=mock_sup.credit_score or 80,
                certifications=mock_sup.certifications or [],
                source="推荐供应商",
                risk_level="低风险" if (mock_sup.credit_score or 0) >= 80 else "中风险",
                credit_score=mock_sup.credit_score
            )
            suppliers.append(match)

    # ==================== 企业信息补充 ====================
    for supplier in suppliers:
        if supplier.credit_score is None:
            try:
                companies = await enterprise_service.search_company(supplier.name)
                if companies:
                    supplier.credit_score = 80 + (hash(supplier.name) % 20)
                    supplier.certifications = ["ISO9001"]
                    supplier.risk_level = "低风险" if supplier.credit_score >= 85 else "中风险"
            except Exception as e:
                print(f"⚠️ 查询企业信息失败: {e}")

    if any(s.credit_score for s in suppliers):
        search_sources.append("企业信息")

    # ==================== 简单排序 ====================
    # 按信用评分排序
    suppliers.sort(key=lambda x: x.credit_score or 0, reverse=True)

    # 按地区筛选
    if request.preferred_regions:
        suppliers = [
            s for s in suppliers
            if any(r in s.region for r in request.preferred_regions)
        ]

    return SourcingResponse(
        material=request.material,
        suppliers=suppliers,
        total_found=len(suppliers),
        search_sources=search_sources,
        search_details=search_details
    )


@router.post("/interview-questions", response_model=InterviewQuestionsResponse)
async def generate_interview_questions(
    request: InterviewQuestionsRequest,
    x_llm_token: Optional[str] = Header(None, alias="X-LLM-Token")
):
    """
    生成面谈问题清单

    根据选中的供应商和物料需求，生成分类面谈问题
    """
    # 构建供应商信息（仅名称）
    supplier_details = [{"name": name} for name in request.suppliers]

    # 调用 LLM 生成问题；未配置时使用模板兜底，保证 Demo 可用
    try:
        if llm_service.is_configured():
            result = await llm_service.generate_interview_questions(
                supplier_details,
                request.material.model_dump(),
                request.focus_areas
            )
        else:
            result = _generate_fallback_interview_questions(
                request.suppliers,
                request.material.model_dump(),
                request.focus_areas
            )

        # 转换为响应格式
        questions_by_supplier = {}
        raw_questions = result.get("questions_by_supplier", {})

        for supplier_name, questions in raw_questions.items():
            interview_questions = []
            for q in questions:
                interview_questions.append(InterviewQuestion(
                    category=q.get("category", "其他"),
                    question=q.get("question", ""),
                    priority=q.get("priority", "medium"),
                    context=q.get("context")
                ))
            questions_by_supplier[supplier_name] = interview_questions

        common_questions = []
        for q in result.get("common_questions", []):
            common_questions.append(InterviewQuestion(
                category=q.get("category", "通用"),
                question=q.get("question", ""),
                priority=q.get("priority", "medium")
            ))

        return InterviewQuestionsResponse(
            questions_by_supplier=questions_by_supplier,
            common_questions=common_questions
        )

    except Exception as e:
        print(f"❌ 生成面谈问题失败: {e}")
        raise HTTPException(status_code=500, detail=f"生成面谈问题失败: {str(e)}")


def _generate_fallback_interview_questions(
    supplier_names: List[str],
    material: dict,
    focus_areas: List[str]
) -> dict:
    """未配置 LLM 时生成基础面谈问题模板"""
    model = material.get("model") or "该物料"
    category = material.get("category") or "相关品类"
    annual_usage = material.get("annual_usage") or "当前预计"
    pain_points = material.get("pain_points") or []
    focus_set = set(focus_areas or [])

    base_questions = [
        {
            "category": "企业基本情况",
            "question": "请介绍贵司在该品类的代理资质、核心团队规模和主要客户案例。",
            "priority": "medium",
            "context": f"用于判断供应商在{category}上的稳定供货能力"
        },
        {
            "category": "产品与质量",
            "question": f"针对{model}，贵司能否提供原厂授权、质量认证、批次追溯和样品测试资料？",
            "priority": "high",
            "context": "确认产品来源、质量体系和可追溯性"
        },
        {
            "category": "商务条款",
            "question": f"按年用量约{annual_usage}计算，贵司可提供的阶梯报价、MOQ、账期和交期分别是多少？",
            "priority": "high" if focus_set & {"价格", "起订量", "交期"} else "medium",
            "context": "用于后续比价和交付风险评估"
        },
        {
            "category": "风险点",
            "question": "若遇到缺货、涨价或交期延误，贵司有哪些替代方案和提前预警机制？",
            "priority": "high",
            "context": "评估供应连续性和异常响应能力"
        }
    ]

    if "技术支持" in focus_set or "服务" in focus_set:
        base_questions.append({
            "category": "服务支持",
            "question": "贵司是否能提供选型建议、FAE 技术支持、售后响应时效和异常处理流程？",
            "priority": "medium",
            "context": "确认采购后的技术与服务保障"
        })

    for pain_point in pain_points:
        base_questions.append({
            "category": "风险点",
            "question": f"我们当前关注“{pain_point}”，贵司有什么具体改善措施或成功案例？",
            "priority": "high",
            "context": "针对当前采购痛点重点追问"
        })

    return {
        "questions_by_supplier": {
            supplier_name: base_questions for supplier_name in supplier_names
        },
        "common_questions": [
            {
                "category": "通用问题",
                "question": "请提供报价有效期、付款条件、交付周期和售后联系人信息。",
                "priority": "medium"
            },
            {
                "category": "通用问题",
                "question": "请说明是否接受小批量试单，以及试单后的批量价格调整规则。",
                "priority": "medium"
            }
        ]
    }