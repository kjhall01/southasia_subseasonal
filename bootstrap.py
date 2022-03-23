import xarray  as xr
from pathlib import Path 
import datetime as dt 
import sys, requests, getpass
from urllib import parse 
import pandas as pd 
threeletters = [None, 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

def download(dest, url, verbose=False, auth='credentials', email='kjhall@iri.columbia.edu', password=None):
    if password is None and auth.upper() == 'CREDENTIALS':
        email = input('Email: ').strip()
        password = getpass.getpass('Password: ')

    url = parse.urlparse(url)
    authorized_url = "{}://{}/auth/login?ver=1&redirect={}&realm=iri.columbia.edu%2Fterms%2Fs2s%2F1".format(url.scheme, url.netloc, parse.quote(url.path, safe=''))

    
    if verbose:
        print('URL: {}'.format(url))
        print('AUTHORIZED: {}'.format(authorized_url))
    
    with requests.Session() as s: 
        r = s.post("https://iridl.ldeo.columbia.edu/auth/login/local/submit/login", data={'email': email, 'password':password, "redirect": url.path })
        #r = s.get(authorized_url, stream=True, allow_redirects=True,  data={'email': email, 'password':password})
        if r.status_code != 200:
            r.raise_for_status()  # Will only raise for 4xx codes, so...
            raise RuntimeError(f"Request to {url} returned status code {r.status_code}")
        #file_size = int(r.headers.get('Content-Length', 0))
        path = Path(dest).expanduser().resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        start, j, total_size = dt.datetime.now(), 0, 0
        if verbose:
            print('DOWNLOADING: [' + ' ' * 25 + '] ({} KB) {}'.format(total_size // 1000, dt.datetime.now() - start), end='\r')
        with path.open("wb") as f:
            for chunk in r.iter_content(16*1024):
                j += 1
                total_size += sys.getsizeof(chunk)
                if verbose:
                    print('\rDOWNLOADING: [' + '*'*j + ' ' * (25 -j ) + '] ({} KB) {}'.format(total_size // 1000, dt.datetime.now() - start), end='\r')
                j = 0 if j >= 25 else j
                f.write(chunk)
    return Path(dest)

def download_ecmwf(extent, target=(14, 28), training_season=None):
    email = input('Email: ').strip()
    password = getpass.getpass('Password: ')


    assert training_season is not None, 'must specify a tuple training season with two pd.Timestamps'
    assert training_season[0].year == training_season[1].year, 'sorry for now, training season cannot be cross-year'
    base = "iridl.ldeo.columbia.edu/SOURCES/.ECMWF/.S2S/.ECMF/.reforecast/.perturbed/.sfc_precip/.tp/"
    base += "S/({} {} {})/({} {} {})/RANGEEDGES/".format(training_season[0].day, threeletters[training_season[0].month], training_season[0].year, training_season[1].day, threeletters[training_season[1].month], training_season[1].year)
    base += "L/{}/{}/VALUES/[L]/differences/".format(target[0], target[1])
    base += "X/{}/{}/RANGEEDGES/Y/{}/{}/RANGEEDGES/".format(extent['west'], extent['east'], extent['south'], extent['north'])

    chunk_files = []
    for year in range(training_season[0].year-20, training_season[0].year):
        url = base + "hdate/({})/VALUES/data.nc".format(year)
        file = download('ecmwf_{}.nc'.format(year), "http://" + parse.quote(url), verbose=True, email=email, password=password)
        chunk_files.append(file)
    chunks = []
    for i, file in enumerate(chunk_files):
        chunk = xr.open_dataset(file, decode_times=False)
        print(chunk)
        chunk.hdate.attrs['calendar'] = '360_day'
        chunk = xr.decode_cf(chunk)
        chunk.coords['S'] = [pd.Timestamp(training_season[0].year-20+i, pd.Timestamp(ii).month, pd.Timestamp(ii).day) for ii in chunk.coords['S'].values]
        chunks.append(chunk.mean('hdate'))
    return xr.concat(chunks, 'S')
