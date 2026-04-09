def add_vendor_column(env):
    env.cr.execute("""
        ALTER TABLE res_partner
        ADD COLUMN IF NOT EXISTS is_vendor_user boolean DEFAULT false;
    """)