from requests import Session
from typing import Union, Dict

from .exceptions import UnsupportedProxyType

def proxy_to_dict(proxy: str) -> Dict[str, str]:
    """Converts a proxy in the format ip:port or ip:port:login:password to a json format

    Args:
        proxy (str): proxy to convert
    
    Returns:
        Dict[str, str]: proxy in json format
    
    Raises:
        UnsupportedProxyType: if the proxy is in a bad format
    
    Example:
        >>> from resilenter_caller import proxy_to_dict
        >>>
        >>> proxy_to_dict("123:123")
        {'http': 'http://123:123', 'https': 'http://123:123'}
        >>> proxy_to_dict("123:123:login:password")
        {'http': 'http://login:password@123:123/', 'https': 'http://login:password@123:123/'}
    """
    proxy_full = proxy.replace('\n','').split(':')
    if len(proxy_full) == 2:
        return {'http': 'http://{}'.format(proxy),'https': 'http://{}'.format(proxy),} 
    elif len(proxy_full) == 4:
        ip_port = '{}:{}'.format(proxy_full[0], proxy_full[1]) 
        login_pw = '{}:{}'.format(proxy_full[2], proxy_full[3])
        return {'http': 'http://{}@{}/'.format(login_pw, ip_port),'https': 'http://{}@{}/'.format(login_pw, ip_port)} 
    else: 
        raise UnsupportedProxyType("Proxy must be in the format ip:port or ip:port:login:password")

def update_session_proxy(session: Session, proxy: Union[str, Dict[str, str]]) -> Union[Dict[str, str], bool]:
    """Updates the proxy of a session, if proxy is a string, it will be converted to a json format

    Args:
        session (Session): session to change
        proxy (Union[str, Dict[str, str]]): proxy to set
    
    Returns:
        Union[dict, bool]: False if proxy is in a bad format
    
    Example:
        >>> from requests import Session
        >>> from resilenter_caller import update_session_proxy
        >>>
        >>> session = Session()
        >>> update_session_proxy(session, "123:123")
        >>> session.proxies
        {'http': 'http://123:123', 'https': 'http://123:123'}
        >>> update_session_proxy(session, "123:123:login:password")
        >>> session.proxies
        {'http': 'http://login:password@123:123/', 'https': 'http://login:password@123:123/'}
    """
    if type(proxy) == str:
        formatted = proxy_to_dict(proxy)
        if not formatted: return False
        session.proxies.update(formatted)
    return proxy