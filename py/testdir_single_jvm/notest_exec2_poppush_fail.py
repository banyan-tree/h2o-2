import unittest, random, sys, time
sys.path.extend(['.','..','../..','py'])
import h2o, h2o_browse as h2b, h2o_exec as h2e, h2o_import as h2i

initList = [
    ('r.hex', 'r.hex=i.hex'),
]

phrases = [
    "r.hex-r.hex;",
    "mean2=function(x){apply(x,1,sum)/nrow(x)};",
    "mean2(r.hex);",
    "r.hex[,ncol(r.hex)+1]=4;",
]

class Basic(unittest.TestCase):
    def tearDown(self):
        h2o.check_sandbox_for_errors()

    @classmethod
    def setUpClass(cls):
        global SEED
        SEED = h2o.setup_random_seed()
        h2o.init(1)

    @classmethod
    def tearDownClass(cls):
        h2o.tear_down_cloud()

    def test_exec2_poppush_fail(self):
        bucket = 'smalldata'
        csvPathname = 'iris/iris2.csv'
        hexKey = 'i.hex'
        parseResult = h2i.import_parse(bucket=bucket, path=csvPathname, schema='put', hex_key=hexKey)

        exprList = []
        while (len(exprList)!=20):
            exprs = [random.choice(phrases) for j in range(random.randint(1,2))]
            # check if we have mean2() before function defn
            functionFound = False
            for e in exprs:
                if 'function' in e:
                    functionFound = True
                if 'mean2' in e and not functionFound:
                    # add the function definition first
                    exprs = ["mean2=function(x){apply(x,1,sum)/nrow(x)};"] + exprs
            exprList.append("".join(exprs))

        # add this one for good measure (known fail)
        exprList += "r.hex-r.hex; mean2=function(x){apply(x,1,sum)/nrow(x)}; mean2(r.hex); r.hex[,ncol(r.hex)+1]=4;"
        exprList += "crunk=function(x){x+98};r.hex[,3]=4;"

        for resultKey, execExpr in initList:
            h2e.exec_expr(h2o.nodes[0], execExpr, resultKey=resultKey, timeoutSecs=4)

        for execExpr in exprList:
            h2e.exec_expr(h2o.nodes[0], execExpr, resultKey=None, timeoutSecs=4)

if __name__ == '__main__':
    h2o.unit_main()
