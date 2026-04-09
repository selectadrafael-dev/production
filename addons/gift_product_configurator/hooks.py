#creating mannual field in db=================
def add_vendor_column(cr, registry):
        cr.execute("""
            ALTER TABLE res_partner
            ADD COLUMN IF NOT EXISTS is_vendor_user boolean DEFAULT false;
        """)