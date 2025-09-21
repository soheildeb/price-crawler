from typing import  
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from itertools import product 
from typing import Any, Dict, Iterable, List


DEFAULT_BASE_URL = "https://irankohan.ir"


def build_session(retries: int = 3, backoff_factor: float = 0.3) -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=(500, 502, 503, 504),
        allowed_methods=frozenset(["GET", "POST"]),
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def _safe_to_int(value) -> Optional[int]:
    """تبدیل ایمن به int؛ اگر قابل تبدیل نیست None برمی‌گرداند."""
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        try:
            return int(float(value))
        except (TypeError, ValueError):
            return None


def calculate(
    session: requests.Session,
    sample_id: int,
    material: int,
    size: int,
    print_kind: int,
    tirazh: int,
    delivery_id: int,
    work_id: int = 3,
    copy_count: int = 0,
    side: int = 1,
    page_count: int = 0,
    base_url: str = DEFAULT_BASE_URL,
    timeout: float = 5.0,
    ) -> int:
    url = f"{base_url}/order/CalculateSamplePrice"
    params = {
        "sampleID": sample_id,
        "workTypeID": work_id,
        "tirazh": 0,
        "tirazhCount": tirazh,
        "printKindID": print_kind,
        "materialID": material,
        "sizeID": size,
        "tool": 0,
        "arz": 0,
        "sideID": side,
        "delivery": delivery_id,
        "copyCount": copy_count,
        "pageCount": page_count,
        "sahafiId": 0,
        "havePrint": "false",
        "haveWrite": "false",
        "MultiLatTypeVal": 0,
        "AttGifID": 0,
    }
    resp = session.get(url, params=params, timeout=timeout)
    resp.raise_for_status()

    j = resp.json()
    raw = _safe_to_int(j)
    if raw is None:
        raise ValueError(f"API returned null or invalid value for sample price \n{params}")

    return raw // 10


def calculate_adt(
    session: requests.Session,
    sampleID: int,
    samplePrintKindID: int,
    sampleMaterialID: int,
    id: int,
    sampleSizeID: int,
    tirazhCount: int,
    deliveryID: int,
    workTypeID: int = 3,
    side: int = 1,
    strCount: str = "_0",
    multiCopyCount: int = 1,
    base_url: str = DEFAULT_BASE_URL,
    timeout: float = 5.0,
) -> int:
    url_adt = f"{base_url}/order/CalculateAdtPrice"
    params = {
        "id": id,
        "workTypeID": workTypeID,
        "count": 1,
        "tirazh": 0,
        "tirazhCount": tirazhCount,
        "deliveryID": deliveryID,
        "strCount": '_یک رو' if side==1 else "'_دو رو'" if side==2 else '_0',
        "MultiLatTypeVal": 0,
        "sampleSizeID": sampleSizeID,
        "tool": 0,
        "arz": 0,
        "sampleID": sampleID,
        "multiCopyCount": multiCopyCount,
        "pageCount": 0,
        "parameterID": 0,
        "side": side,
        "sahafiId": 0,
        "sampleMaterialID": sampleMaterialID,
        "samplePrintKindID": samplePrintKindID,
    }
    resp = session.get(url_adt, params=params, timeout=timeout)
    resp.raise_for_status()

    j = resp.json()
    raw = _safe_to_int(j)
    if raw is None:
        raise ValueError(f"API returned null or invalid value for adt price \n{params}")

    return raw // 10

def _normalize_options(v: Any) -> List[Any]:
    if isinstance(v, dict):
        return list(v.keys())
    if isinstance(v, (list, tuple, set)):
        return list(v)
    return [v]

def generate_combinations(product_config: Dict[str, Any], include_singletons_in_display: bool = False):
    keys = list(product_config.keys())
    options_list = [_normalize_options(product_config[k]) for k in keys]

    for combo in product(*options_list):
        params_api = dict(zip(keys, combo))
        params_display = {}

        for k, chosen in params_api.items():
            original = product_config[k]
            if isinstance(original, dict):
                params_display[k] = original[chosen]
            elif isinstance(original, (list, tuple, set)):
                if include_singletons_in_display or len(original) > 1:
                    params_display[k] = chosen
            else:
                if include_singletons_in_display:
                    params_display[k] = chosen

        yield params_api, params_display