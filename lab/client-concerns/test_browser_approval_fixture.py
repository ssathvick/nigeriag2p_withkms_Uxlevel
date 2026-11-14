from pathlib import Path
import test_location_import_e2e as e
e.HOST='https://g2p-register.wverve.in'
e.WORK=Path(__file__).parent/'browser-approval-verification'
e.WORK.mkdir(exist_ok=True)
e.STATE=e.WORK/'state.json'
if __name__=='__main__':e.run()
