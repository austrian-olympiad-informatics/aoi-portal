export interface ProfileInfoResponse {
  first_name: string;
  last_name: string;
  email: string;
  is_admin: boolean;
  birthday: string | null;
  phone_nr: string | null;
  address_street: string | null;
  address_zip: string | null;
  address_town: string | null;
  school_name: string | null;
  school_address: string | null;
  eligibility: string | null;
}

export interface ProfileUpdateParams {
  first_name?: string;
  last_name?: string;
  birthday?: string | null;
  phone_nr?: string | null;
  address_street?: string | null;
  address_zip?: string | null;
  address_town?: string | null;
  school_name?: string | null;
  school_address?: string | null;
  eligibility?: string | null; 
}
